from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
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

		return metrics

	def get_context_data(self, *args, **kwargs):
		context = super().get_context_data(*args, **kwargs)
		context["metrics"] = self.get_metrics()
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
