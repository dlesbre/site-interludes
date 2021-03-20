from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.db.models import Count
from django.forms import formset_factory
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import RedirectView, UpdateView, TemplateView, View

from accounts.models import EmailUser
from home.models import ActivityList, InterludesActivity, InterludesParticipant
from home.forms import ActivityForm, BaseActivityFormSet, InscriptionForm
from site_settings.models import SiteSettings
from shared.views import CSVWriteView, SuperuserRequiredMixin


# ==============================
# Site static pages
# ==============================


class HomeView(TemplateView):
	"""Vue pour la page d'acceuil"""
	template_name = "home.html"


class ActivityView(TemplateView):
	"""Vue pour la liste des activités"""
	template_name = "activites.html"

	def get_context_data(self, **kwargs):
		"""ajoute la liste des activités au contexte"""
		context = super(ActivityView, self).get_context_data(**kwargs)
		settings = SiteSettings.load()
		context['activities'] = InterludesActivity.objects.filter(display=True).order_by("title")
		context['planning'] = InterludesActivity.objects.filter(on_planning=True).order_by("title")
		context['friday'] = settings.date_start.day
		context['saturday'] = (settings.date_start + timedelta(days=1)).day
		context['sunday'] = (settings.date_start + timedelta(days=2)).day
		return context


class FAQView(TemplateView):
	"""Vue pour la FAQ"""
	template_name = "faq.html"


# ==============================
# Registration
# ==============================


class RegisterClosed(TemplateView):
	"""Vue pour quand les inscriptions ne sont pas ouvertes"""
	template_name = "inscription/closed.html"

class RegisterSignIn(TemplateView):
	"""Vue affichée quand les inscriptions sont ouverte mais
	l'utilisateur n'est pas connecté"""
	template_name = "inscription/signin.html"

class RegisterUpdateView(LoginRequiredMixin, TemplateView):
	"""Vue pour s'inscrire et modifier son inscription"""
	template_name = "inscription/form.html"
	form_class = InscriptionForm
	formset_class = formset_factory(form=ActivityForm, extra=3, formset=BaseActivityFormSet)

	@staticmethod
	def get_activities(participant):
		activities = ActivityList.objects.filter(participant=participant).order_by("priority")
		return [{"activity": act.activity} for act in activities]

	@staticmethod
	def set_activities(participant, formset):
		# delete old activites
		ActivityList.objects.filter(participant=participant).delete()

		priority = 0
		for form in formset:
			data = form.cleaned_data
			if data:
				activity = data["activity"]
				ActivityList(priority=priority, participant=participant, activity=activity).save()
				priority += 1

	def get(self, request, *args, **kwargs):
		participant = request.user.profile
		activities = self.get_activities(participant)
		form = self.form_class(instance=participant)
		formset = self.formset_class(initial=activities)
		context = {"form": form, "formset": formset}
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST, instance=request.user.profile)
		formset = self.formset_class(request.POST)
		if not (form.is_valid() and formset.is_valid()):
			context = {"form": form, "formset": formset}
			return render(request, self.template_name, context)

		form.save()
		self.set_activities(request.user.profile, formset)

		messages.success(request, "Votre inscription a bien été enregistrée")
		return redirect("accounts:profile", permanent=False)

class RegisterView(View):
	"""Vue pour l'inscription
	repartie sur les vue RegisterClosed, RegisterSignIn et RegisterUpdateView"""
	def dispatch(self, request, *args, **kwargs):
		settings = SiteSettings.load()
		if not settings.inscriptions_open:
			return RegisterClosed.as_view()(request)
		if not request.user.is_authenticated:
			return RegisterSignIn.as_view()(request)
		return RegisterUpdateView.as_view()(request)


class UnregisterView(LoginRequiredMixin, RedirectView):
	pattern_name = "accounts:profile"

	def get_redirect_url(self, *args, **kwargs):
		participant = self.request.user.profile
		participant.is_registered = False
		participant.save()
		messages.success(self.request, "Vous avez été désinscrit")
		return reverse(self.pattern_name)


# ==============================
# Admin views
# ==============================


class AdminView(SuperuserRequiredMixin, TemplateView):
	template_name = "admin.html"

	def get_metrics(self):
		registered = InterludesParticipant.objects.filter(is_registered = True)
		acts = InterludesActivity.objects.all()
		wishes = ActivityList.objects.filter(participant__is_registered=True)
		class metrics:
			participants = registered.count()
			ulm = registered.filter(school="U").count()
			lyon = registered.filter(school="L").count()
			rennes = registered.filter(school="R").count()
			saclay = registered.filter(school="P").count()
			non_registered = EmailUser.objects.filter(is_active=True).count() - participants

			meal1 = registered.filter(meal_friday_evening=True).count()
			meal2 = registered.filter(meal_saturday_morning=True).count()
			meal3 = registered.filter(meal_saturday_midday=True).count()
			meal4 = registered.filter(meal_saturday_evening=True).count()
			meal5 = registered.filter(meal_sunday_morning=True).count()
			meal6 = registered.filter(meal_sunday_midday=True).count()
			meals = meal1 + meal2 + meal3 + meal4 + meal5 + meal6

			# mugs = registered.filter(mug=True).count()
			sleeps = registered.filter(sleeps=True).count()

			activites = acts.count()
			act_ins = acts.filter(must_subscribe=True).count()
			wish = wishes.count()
			granted = wishes.filter(accepted=True).count()

		# validation de la repartition des activités
		accepted = wishes.filter(accepted=True)
		# order_by is useless but required
		counts = accepted.values("activity").annotate(total=Count("id")).order_by("activity")

		return metrics

	def validate_activity_participant_nb(self):
		""" Vérifie que le nombre de participant inscrit
		à chaque activité est compris entre le min et le max"""
		activities = InterludesActivity.objects.filter(must_subscribe=True, display=True)
		min_fails = ""
		max_fails = ""
		for act in activities:
			total = ActivityList.objects.filter(
				activity=act, accepted=True, participant__is_registered=True
			).aggregate(total=Count("id"))["total"]
			max = act.max_participants
			min = act.min_participants
			if max != 0 and max < total:
				max_fails += "<br> &bullet;&ensp;{}: {} inscrits (maximum {})".format(
					act.title, total, max
				)
			if min > total:
				min_fails += "<br> &bullet;&ensp;{}: {} inscrits (minimum {})".format(
					act.title, total, max
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
		activities = InterludesActivity.objects.filter(must_subscribe=True, display=True)
		conflicts = []
		for i, act1 in enumerate(activities):
			for act2 in activities[i+1:]:
				if act1.conflicts(act2):
					conflicts.append((act1, act2))
		base_qs = ActivityList.objects.filter(accepted=True, participant__is_registered=True)
		errors = ""
		for act1, act2 in conflicts:
			participants1 = base_qs.filter(activity=act1).values("participant")
			participants2 = base_qs.filter(activity=act1).values("participant")
			intersection = participants1 & participants2
			if intersection:
				print(intersection)
				errors += '<br> &bullet;&ensp; {} participe(nt) à la fois à "{}" et à "{}"'.format(
					",".join(str(InterludesParticipant.objects.get(id=x["participant"])) for x in intersection),
					act1.title, act2.title
				)

		if errors:
			return '<li class="error">Des participants ont plusieurs activités au même moment :{}</li>'.format(
				errors
			)
		return '<li class="success">Aucun inscrit à plusieurs activités simultanées</li>'

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
		validations += '</ul>'

		user_email_nb = ActivityList.objects.filter(
			participant__is_registered=True
		).values("participant").distinct().count()
		orga_email_nb = InterludesActivity.objects.filter(
			display=True, must_subscribe=True, communicate_participants=True
		).count()

		return {
			"validations": validations,
			"user_email_nb": user_email_nb,
			"orga_email_nb": orga_email_nb,
			"validation_errors": '<li class="error">' in validations
		}

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["metrics"] = self.get_metrics()
		context.update(self.validate_activity_allocation())
		return context


class ExportActivities(SuperuserRequiredMixin, CSVWriteView):
	filename = "activites_interludes"
	model = InterludesActivity

class ExportParticipants(SuperuserRequiredMixin, CSVWriteView):
	filename = "participants_interludes"
	headers = [
		"id", "mail", "prénom", "nom", "ENS", "Dors sur place", "Tasse",
		"Repas vendredi", "Repas S matin", "Repas S midi", "Repas S soir",
		"Repas D matin", "Repas D soir"
	]
	def get_rows(self):
		profiles = InterludesParticipant.objects.filter(is_registered=True).all()
		rows = []
		for profile in profiles:
			rows.append([
				profile.user.id,
				profile.user.email,
				profile.user.first_name,
				profile.user.last_name,
				profile.school,
				profile.sleeps,
				profile.mug,
				profile.meal_friday_evening,
				profile.meal_saturday_morning,
				profile.meal_saturday_midday,
				profile.meal_saturday_evening,
				profile.meal_sunday_morning,
				profile.meal_sunday_midday,
			])
		return rows

class ExportActivityChoices(SuperuserRequiredMixin, CSVWriteView):
	filename = "choix_activite_interludes"
	model = ActivityList
	headers = ["id_participant", "nom_participant", "priorité", "nom_activité", "id_activité"]

	def get_rows(self):
		activities = ActivityList.objects.all()
		rows = []
		for act in activities:
			if act.participant.is_registered:
				rows.append([
					act.participant.id, str(act.participant), act.priority,
					str(act.activity), act.activity.id
				])
		return rows

# ==============================
# Sitemap
# ==============================


class StaticViewSitemap(Sitemap):
	"""Vue générant la sitemap.xml du site"""
	changefreq = 'monthly'

	def items(self):
		"""list of pages to appear in sitemap"""
		return ["home", "inscription", "activites", "FAQ"]

	def location(self, item):
		"""real url of an item"""
		return reverse(item)

	def priority(self, obj):
		"""priority to appear in sitemap"""
		# Priorize home page over the rest in search results
		if obj == "home" or obj == "":
				return 0.8
		else:
			return None # defaults to 0.5 when unset
