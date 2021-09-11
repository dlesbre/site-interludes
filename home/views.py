from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.forms import formset_factory
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import RedirectView, TemplateView, View

from home import models
from home.forms import ActivityForm, BaseActivityFormSet, InscriptionForm
from site_settings.models import SiteSettings


# ==============================
# Site static pages
# ==============================


class HomeView(TemplateView):
	"""Vue pour la page d'acceuil"""
	template_name = "home.html"

def get_planning_context():
	"""Returns the context dict needed to display the planning"""
	settings = SiteSettings.load()
	context = dict()
	context['planning'] = models.InterludesSlot.objects.filter(on_planning=True).order_by("title")
	if settings.date_start is not None:
		context['friday'] = settings.date_start.day
		context['saturday'] = (settings.date_start + timedelta(days=1)).day
		context['sunday'] = (settings.date_start + timedelta(days=2)).day
	else:
		context['friday'] = 1
		context['saturday'] = 2
		context['sunday'] = 3
	return context

class ActivityView(TemplateView):
	"""Vue pour la liste des activités"""
	template_name = "activites.html"

	def get_context_data(self, **kwargs):
		"""ajoute la liste des activités au contexte"""
		context = super(ActivityView, self).get_context_data(**kwargs)
		context['activities'] = models.InterludesActivity.objects.filter(display=True).order_by("title")
		context.update(get_planning_context())
		return context


class FAQView(TemplateView):
	"""Vue pour la FAQ"""
	template_name = "faq-distanciel.html"


# ==============================
# Profile and registration
# ==============================


class ProfileView(LoginRequiredMixin, TemplateView):
	"""Vue des actions de gestion de son profil"""
	template_name = "profile.html"
	redirect_field_name = "next"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		settings = SiteSettings.load()
		if settings.activities_allocated:
			my_choices = models.InterludesActivityChoices.objects.filter(
				participant=self.request.user.profile,
				accepted=True
			)
		else:
			my_choices = models.InterludesActivityChoices.objects.filter(
				participant=self.request.user.profile
			)

		context["my_choices"] = my_choices
		return context


class RegisterClosed(TemplateView):
	"""Vue pour quand les inscriptions ne sont pas ouvertes"""
	template_name = "inscription/closed.html"

class RegisterSignIn(TemplateView):
	"""Vue affichée quand les inscriptions sont ouverte mais
	l'utilisateur n'est pas connecté"""
	template_name = "inscription/signin.html"

class RegisterUpdateView(LoginRequiredMixin, TemplateView):
	"""Vue pour s'inscrire et modifier son inscription"""
	template_name = "inscription/form-distanciel.html"
	form_class = InscriptionForm
	formset_class = formset_factory(form=ActivityForm, extra=3, formset=BaseActivityFormSet)

	@staticmethod
	def get_slots(participant):
		activities = models.InterludesActivityChoices.objects.filter(participant=participant).order_by("priority")
		return [{"slot": act.slot} for act in activities]

	@staticmethod
	def set_activities(participant, formset):
		# delete old activites
		models.InterludesActivityChoices.objects.filter(participant=participant).delete()

		priority = 0
		for form in formset:
			data = form.cleaned_data
			if data:
				slot = data["slot"]
				models.InterludesActivityChoices(
					priority=priority, participant=participant, slot=slot
				).save()
				priority += 1

	def get(self, request, *args, **kwargs):
		participant = request.user.profile
		slots = self.get_slots(participant)
		form = self.form_class(instance=participant)
		formset = self.formset_class(initial=slots)
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
		return redirect("profile", permanent=False)

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
	pattern_name = "profile"

	def get_redirect_url(self, *args, **kwargs):
		participant = self.request.user.profile
		participant.is_registered = False
		participant.save()
		messages.success(self.request, "Vous avez été désinscrit")
		return reverse(self.pattern_name)


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
