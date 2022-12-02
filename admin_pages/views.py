from django.conf import settings
from django.contrib import messages
from django.core.mail import mail_admins, send_mass_mail
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView

from accounts.models import EmailUser
from home import models
from home.views import get_planning_context
from site_settings.models import Colors, SiteSettings
from shared.views import CSVWriteView, SuperuserRequiredMixin

from admin_pages.forms import Recipients, SendEmailForm

# ==============================
# Main Admin views
# ==============================


class AdminView(SuperuserRequiredMixin, TemplateView):
	template_name = "admin.html"

	def get_metrics(self):
		registered = models.ParticipantModel.objects.filter(
			is_registered=True, user__is_active=True
		)
		acts = models.ActivityModel.objects.all()
		slots_in = models.SlotModel.objects.all()
		wishes = models.ActivityChoicesModel.objects.filter(
			participant__is_registered=True, participant__user__is_active=True
		)
		class metrics:
			participants = registered.count()
			ulm = registered.filter(school=models.ParticipantModel.ENS.ENS_ULM).count()
			lyon = registered.filter(school=models.ParticipantModel.ENS.ENS_LYON).count()
			rennes = registered.filter(school=models.ParticipantModel.ENS.ENS_RENNES).count()
			saclay = registered.filter(school=models.ParticipantModel.ENS.ENS_CACHAN).count()
			non_registered = EmailUser.objects.filter(is_active=True).count() - participants
			# mugs = registered.filter(mug=True).count()
			sleeps = registered.filter(sleeps=True).count()

			meal1 = registered.filter(meal_friday_evening=True).count()
			meal2 = registered.filter(meal_saturday_morning=True).count()
			meal3 = registered.filter(meal_saturday_midday=True).count()
			meal4 = registered.filter(meal_saturday_evening=True).count()
			meal5 = registered.filter(meal_sunday_morning=True).count()
			meal6 = registered.filter(meal_sunday_midday=True).count()
			meals = meal1 + meal2 + meal3 + meal4 + meal5 + meal6

			activites = acts.count()
			displayed = acts.filter(display=True).count()
			act_ins = acts.filter(display=True, must_subscribe=True).count()
			communicate = acts.filter(communicate_participants=True).count()
			st_present = acts.filter(display=True, status=models.ActivityModel.Status.PRESENT).count()
			st_distant = acts.filter(display=True, status=models.ActivityModel.Status.DISTANT).count()
			st_both = acts.filter(display=True, status=models.ActivityModel.Status.BOTH).count()

			slots = slots_in.count()
			true_ins = slots_in.filter(subscribing_open=True).count()
			wish = wishes.count()
			granted = wishes.filter(accepted=True).count()
			malformed = models.ActivityChoicesModel.objects.filter(slot__subscribing_open=False).count()

		return metrics

	def validate_activity_participant_nb(self):
		""" Vérifie que le nombre de participant inscrit
		à chaque activité est compris entre le min et le max"""
		slots = models.SlotModel.objects.filter(subscribing_open=True)
		min_fails = ""
		max_fails = ""
		for slot in slots:
			total = models.ActivityChoicesModel.objects.filter(
				slot=slot, accepted=True, participant__is_registered=True,
				participant__user__is_active=True
			).aggregate(total=Count("id"))["total"]
			max = slot.activity.max_participants
			min = slot.activity.min_participants
			if max != 0 and max < total:
				max_fails += "<br> &bullet;&ensp;{}: {} inscrits (maximum {})".format(
					slot, total, max
				)
			if min > total:
				min_fails += "<br> &bullet;&ensp;{}: {} inscrits (minimum {})".format(
					slot, total, min
				)
		message = ""
		if min_fails:
			message += '<li class="error">Activités en sous-effectif : {}</li>'.format(min_fails)
		else:
			message += '<li class="success">Aucune activité en sous-effectif</li>'
		if max_fails:
			message += '<li class="error">Activités en sur-effectif : {}</li>'.format(max_fails)
		else:
			message += '<li class="success">Aucune activité en sur-effectif</li>'
		return message

	def validate_activity_conflicts(self):
		"""Vérifie que personne n'est inscrit à des activités simultanées"""
		slots = models.SlotModel.objects.filter(subscribing_open=True)
		conflicts = []
		for i, slot_1 in enumerate(slots):
			for slot_2 in slots[i+1:]:
				if slot_1.conflicts(slot_2):
					conflicts.append((slot_1, slot_2))
		base_qs = models.ActivityChoicesModel.objects.filter(
			accepted=True, participant__is_registered=True,
			participant__user__is_active=True
		)
		errors = ""
		for slot_1, slot_2 in conflicts:
			participants_1 = {x.participant for x in base_qs.filter(slot=slot_1)}
			participants_2 = {x.participant for x in base_qs.filter(slot=slot_2)}
			intersection = participants_1.intersection(participants_2)
			if intersection:
				errors += '<br> &bullet;&ensp; {} participe à la fois à "{}" et à "{}"'.format(
					", ".join(str(x) for x in intersection), slot_1, slot_2
				)

		if errors:
			return '<li class="error">Des participants ont plusieurs activités au même moment :{}</li>'.format(
				errors
			)
		return '<li class="success">Aucun inscrit à plusieurs activités simultanées</li>'

	def validate_slot_less(self):
		"""verifie que toutes les activité demandant une liste de participant ont un créneaux"""
		activities = models.ActivityModel.objects.filter(communicate_participants=True)
		errors = ""
		for activity in activities:
			count = models.SlotModel.objects.filter(activity=activity).count()
			if count == 0:
				errors += "<br> &bullet;&ensp; {}".format(activity.title)
		if errors:
			return '<li class="error">Certaines activités demandant une liste de participants n\'ont pas de créneaux :{}<br>Leurs orgas vont recevoir un mail inutile.</li>'.format(
				errors
			)
		return '<li class="success">Toutes les activités demandant une liste de participants ont au moins un créneau</li>'

	def validate_multiple_similar_inscription(self):
		"""verifie que personne n'est inscrit à la même activité plusieurs fois"""
		slots = models.SlotModel.objects.filter(subscribing_open=True)
		conflicts = []
		for i, slot_1 in enumerate(slots):
			for slot_2 in slots[i+1:]:
				if slot_1.activity == slot_2.activity:
					conflicts.append((slot_1, slot_2))
		base_qs = models.ActivityChoicesModel.objects.filter(
			accepted=True, participant__is_registered=True,
			participant__user__is_active=True
		)
		errors = ""
		for slot_1, slot_2 in conflicts:
			participants_1 = {x.participant for x in base_qs.filter(slot=slot_1)}
			participants_2 = {x.participant for x in base_qs.filter(slot=slot_2)}
			intersection = participants_1.intersection(participants_2)
			if intersection:
				errors += '<br> &bullet;&ensp; {} inscrit aux créneaux "{}" et  "{}" de l\'activité "{}"'.format(
					", ".join(str(x) for x in intersection), slot_1, slot_2, slot_1.activity
				)

		if errors:
			return '<li class="error">Des participants sont inscrits plusieurs fois à la même activité :{}</li>'.format(
				errors
			)
		return '<li class="success">Aucun inscrit plusieurs fois à une même activité</li>'

	def planning_validation(self):
		"""Vérifie que toutes les activités ont le bon nombre de créneaux
		dans le planning"""
		errors = ""
		activities = models.ActivityModel.objects.all()
		for activity in activities:
			nb_wanted = activity.desired_slot_nb
			nb_got = activity.slots.count()
			if nb_wanted != nb_got:
				errors += '<br> &bullet;&ensp; "{}" souhaite {} crénaux mais en a {}.'.format(
					activity.title, nb_wanted, nb_got
				)
		if errors:
			return '<li class="error">Certaines activités ont trop/pas assez de crénaux :{}</li>'.format(
				errors
			)
		return '<li class="success">Toutes les activités ont le bon nombre de crénaux</li>'

	def validate_activity_allocation(self):
		settings = SiteSettings.load()
		validations = '<ul class="messagelist">'

		# validate global settings
		if not settings.inscriptions_open:
			validations += '<li class="success">Les inscriptions sont fermées</li>'
		else:
			validations += '<li class="error">Les inscriptions sont encores ouvertes</li>'
		if settings.activities_allocated:
			validations += '<li class="success">La répartition est marquée comme effectuée</li>'
		else:
			validations += '<li class="error">La répartition n\'est pas marquée comme effectuée</li>'

		# longer validations
		validations += self.validate_activity_participant_nb()
		validations += self.validate_activity_conflicts()
		validations += self.validate_multiple_similar_inscription()
		validations += self.validate_slot_less()

		if settings.discord_link:
			validations += '<li class="success">Le lien du discord est renseigné</li>'
		else:
			validations += '<li class="error">Le lien du discord n\'est pas renseigné</li>'

		validations += '</ul>'

		user_email_nb = models.ParticipantModel.objects.filter(
			is_registered=True, user__is_active=True
		).count()
		orga_email_nb = models.ActivityModel.objects.filter(
			communicate_participants=True
		).count()

		return {
			"validations": validations,
			"user_email_nb": user_email_nb,
			"orga_email_nb": orga_email_nb,
			"validation_errors": '<li class="error">' in validations,
			"planning_validation": self.planning_validation(),
		}

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["metrics"] = self.get_metrics()
		context.update(get_planning_context())
		context.update(self.validate_activity_allocation())
		return context


# ==============================
# DB Export Views
# ==============================


class ExportActivities(SuperuserRequiredMixin, CSVWriteView):
	filename = "activites_interludes"
	model = models.ActivityModel
	fields = [
		# The key is "host_id" but listed as "host" in auto-found field names
		# which leads to an error...
		'id', 'display', 'title', 'act_type', 'game_type', 'description',
		'desc_as_html', 'host_id', 'host_name', 'host_email', 'host_info', 'show_email',
		'must_subscribe', 'communicate_participants', 'max_participants',
		'min_participants', 'duration', 'desired_slot_nb',
		'available_friday_evening', 'available_friday_night',
		'available_saturday_morning', 'available_saturday_afternoon',
		'available_saturday_evening', 'available_saturday_night',
		'available_sunday_morning', 'available_sunday_afternoon',
		'constraints', 'status', 'needs', 'comments'
	]

class ExportSlots(SuperuserRequiredMixin, CSVWriteView):
	filename = "créneaux_interludes"
	headers = [
		"Titre", "Début", "Salle",
		"Ouverte aux inscriptions", "Affiché sur le planning", "Affiché sur l'activité",
		"Couleur", "Durée", "Durée activité",
	]

	def get_rows(self):
		slots = models.SlotModel.objects.all()
		rows = []
		for slot in slots:
			rows.append([
				str(slot), slot.start, slot.room,
				slot.subscribing_open, slot.on_planning, slot.on_activity,
				Colors(slot.color).name, slot.duration, slot.activity.duration,
			])
		return rows

class ExportParticipants(SuperuserRequiredMixin, CSVWriteView):
	filename = "participants_interludes"
	headers = [
		"id", "mail", "prénom", "nom", "ENS", "Salarié", "Dors sur place", #"Tasse",
		"Nombre de repas", "Repas vendredi", "Repas S matin", "Repas S midi", "Repas S soir",
		"Repas D matin", "Repas D soir", "Nombre murders", "Commentaires"
	]
	def get_rows(self):
		profiles = models.ParticipantModel.objects.filter(
			is_registered=True,user__is_active=True
		).all()
		rows = []
		for profile in profiles:
			rows.append([
				profile.user.id,
				profile.user.email,
				profile.user.first_name,
				profile.user.last_name,
				profile.school,
				profile.paid,
				profile.sleeps,
				# profile.mug,
				profile.nb_meals,
				profile.meal_friday_evening,
				profile.meal_saturday_morning,
				profile.meal_saturday_midday,
				profile.meal_saturday_evening,
				profile.meal_sunday_morning,
				profile.meal_sunday_midday,
				profile.nb_murder,
				profile.comment,
			])
		return rows

class ExportActivityChoices(SuperuserRequiredMixin, CSVWriteView):
	filename = "choix_activite_interludes"
	model = models.ActivityChoicesModel
	headers = ["id_participant", "nom_participant", "mail_participant", "priorité", "obtenu", "nom_créneau", "id_créneau"]

	def get_rows(self):
		activities = models.ActivityChoicesModel.objects.all()
		rows = []
		for act in activities:
			if act.participant.is_registered and act.participant.user.is_active:
				rows.append([
					act.participant.id, str(act.participant), act.participant.user.email, act.priority,
					act.accepted, str(act.slot), act.slot.id
				])
		return rows


# ==============================
# Send email views
# ==============================


class SendEmailBase(SuperuserRequiredMixin, RedirectView):
	"""Classe abstraite pour l'envoie d'un groupe d'emails"""
	pattern_name = "admin_pages:index"
	from_address = None

	def send_emails(self):
		raise NotImplementedError("{}.send_emails isn't implemented".format(self.__class__.__name__))

	def get_redirect_url(self, *args, **kwargs):
		settings = SiteSettings.load()
		if settings.allow_mass_mail:
			self.send_emails()
		else:
			messages.error(self.request, "L'envoi de mail de masse est désactivé dans les réglages")
		return reverse(self.pattern_name)

class SendUserEmail(SendEmailBase):
	"""Envoie aux utilisateurs leur repartition d'activité"""

	def get_emails(self):
		"""genere les mails a envoyer"""
		participants = models.ParticipantModel.objects.filter(
			is_registered=True, participant__user__is_active=True
		)
		emails = []
		settings = SiteSettings.load()
		for participant in participants:
			my_choices = models.ActivityChoicesModel.objects.filter(participant=participant)
			message = render_to_string("email/user.html", {
				"user": participant.user,
				"settings": settings,
				"requested_activities_nb": my_choices.count(),
				"my_choices": my_choices.filter(accepted=True),
			})
			emails.append((
				settings.USER_EMAIL_SUBJECT_PREFIX + "Vos activités", # subject
				message,
				self.from_address, # From:
				[participant.user.email], # To:
			))
		return emails

	def send_emails(self):
		settings = SiteSettings.load()
		if settings.user_notified:
			messages.error(self.request, "Les participants ont déjà reçu un mail annonçant la répartition. Modifiez les réglages pour en envoyer un autre")
			return
		settings.user_notified = True
		settings.save()
		emails = self.get_emails()

		nb_sent = send_mass_mail(emails, fail_silently=False)
		mail_admins(
			"Emails de répartition envoyés aux participants",
			"Les participants ont reçu un mail leur communiquant la répartition des activités\n"
			"Nombre total de mail envoyés: {}\n\n"
			"{}".format(nb_sent, settings.EMAIL_SIGNATURE)
		)
		messages.success(self.request, "{} mails envoyés aux utilisateurs".format(nb_sent))

class SendOrgaEmail(SendEmailBase):
	"""
	Envoie aux organisateur leur communiquant les nom/mail des inscrits
	à leurs activités
	"""

	def get_emails(self):
		"""genere les mails a envoyer"""
		activities = models.ActivityModel.objects.filter(communicate_participants=True)
		emails = []
		settings = SiteSettings.load()
		for activity in activities:
			slots = models.SlotModel.objects.filter(activity=activity)
			message = render_to_string("email/orga.html", {
				"activity": activity,
				"settings": settings,
				"slots": slots,
			})
			emails.append((
				settings.USER_EMAIL_SUBJECT_PREFIX +
				"Liste d'inscrits à votre activité {}".format(activity.title), # subject
				message,
				self.from_address, # From:
				[activity.host_email] # To:
			))
		return emails

	def send_emails(self):
		settings = SiteSettings.load()
		if settings.orga_notified:
			messages.error(self.request, "Les orgas ont déjà reçu un mail avec leur listes d'inscrits. Modifiez les réglages pour en envoyer un autre")
			return
		settings.orga_notified = True
		settings.save()
		emails = self.get_emails()

		nb_sent = send_mass_mail(emails, fail_silently=False)
		mail_admins(
			"Listes d'inscrits envoyés aux orgas",
			"Les mails communiquant aux organisateurs leur listes d'inscrit ont été envoyés\n"
			"Nombre total de mail envoyés: {}\n\n"
			"{}".format(nb_sent, settings.EMAIL_SIGNATURE)
		)
		messages.success(self.request, "{} mails envoyés aux orgas".format(nb_sent))


class NewEmail(SuperuserRequiredMixin, FormView):
	"""Créer un nouveau mail"""
	template_name = "send_email.html"
	form_class = SendEmailForm
	success_url = reverse_lazy("admin_pages:index")
	from_address = None

	def get_emails(self, selection):
		"""return the list of destination emails"""
		if selection == Recipients.ALL:
			users = EmailUser.objects.filter(is_active=True)
			return [u.email for u in users]
		elif selection == Recipients.REGISTERED:
			participants = models.ParticipantModel.objects.filter(
				is_registered=True, user__is_active=True
			)
			return [p.user.email for p in participants]
		else:
			raise ValueError("Invalid selection specifier\n")

	@staticmethod
	def sending_allowed():
		"""Checks if sending mass emails is allowed"""
		settings = SiteSettings.load()
		return settings.allow_mass_mail

	def form_valid(self, form):
		# This method is called when valid form data has been POSTed.
		# It should return an HttpResponse.
		if not self.sending_allowed():
			messages.error(request, "L'envoi de mail de masse est désactivé dans les réglages")
		else:
			dest = form.cleaned_data["dest"]
			subject = form.cleaned_data["subject"]
			text = form.cleaned_data["text"]
			emails = []
			for to_addr in self.get_emails(dest):
				emails.append([
					subject,
					text,
					self.from_address,
					[to_addr]
				])
			nb_sent = send_mass_mail(emails, fail_silently=False)
			mail_admins(
				"Email envoyé",
				"Un email a été envoyé à {}.\n"
				"Nombre total de mail envoyés: {}\n\n"
				"Sujet : {}\n\n"
				"{}\n\n"
				"{}".format(
					Recipients(dest).label, nb_sent, subject, text,
					settings.EMAIL_SIGNATURE
				)
			)
			messages.success(self.request, "{} mails envoyés".format(nb_sent))
		return super().form_valid(form)

	def get_context_data(self, *args, **kwargs):
		"""ajoute l'email d'envoie aux données contextuelles"""
		context = super().get_context_data(*args, **kwargs)
		context["from_email"] = self.from_address if self.from_address else settings.DEFAULT_FROM_EMAIL
		context["registered_nb"] =  models.ParticipantModel.objects.filter(
			is_registered = True, user__is_active=True
		).count()
		context["accounts_nb"] = EmailUser.objects.filter(is_active=True).count()
		return context

	def get(self, request, *args, **kwargs):
		if self.sending_allowed():
			return super().get(request, *args, **kwargs)
		messages.error(request, "L'envoi de mail de masse est désactivé dans les réglages")
		return HttpResponseRedirect(self.get_success_url())
