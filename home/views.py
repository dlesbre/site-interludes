from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.forms import modelformset_factory
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import UpdateView, TemplateView, View

from home.models import ActivityList, InterludesActivity
from home.forms import ActivityForm, InscriptionForm
from site_settings.models import SiteSettings


class HomeView(TemplateView):
	"""Vue pour la page d'acceuil"""
	template_name = "home.html"


class ActivityView(TemplateView):
	"""Vue pour la liste des activités"""
	template_name = "activites.html"

	def get_context_data(self, **kwargs):
		"""ajoute la liste des activités au contexte"""
		context = super(ActivityView, self).get_context_data(**kwargs)
		context['activities'] = InterludesActivity.objects.filter(display=True).order_by("title")
		return context


class FAQView(TemplateView):
	"""Vue pour la FAQ"""
	template_name = "faq.html"


class RegisterClosed(TemplateView):
	"""Vue pour quand les inscriptions ne sont pas ouvertes"""
	template_name = "inscription/closed.html"

class RegisterSignIn(TemplateView):
	"""Vue affichée quand les inscriptions sont ouverte mais
	l'utilisateur n'est pas connecté"""
	template_name = "inscription/signin.html"

class RegisterUpdateView(LoginRequiredMixin, UpdateView):
	"""Vue pour s'inscrire et modifier son inscription"""
	template_name = "inscription/form.html"
	form_class = InscriptionForm
	formset = modelformset_factory(ActivityList, form=ActivityForm, extra=3)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["formset"] = self.formset(queryset=ActivityList.objects.none())
		return context

	def get_object(self):
		return self.request.user.profile

	def get_success_url(self):
		return reverse("accounts:profile")

	def form_valid(self, form):
		messages.success(self.request, "Votre inscription a été enregistrée")
		return super().form_valid(form)

	def post(self, request, *args, **kwargs):
		form = self.form_class(request.POST)
		formset = self.formset(request.POST)
		if formset.is_valid():
			print("\n\n{} {}\n\n".format(len(formset), formset))
		else:
			print("\n\nInvalid\n\n")
		return super().post(request, *args, **kwargs)

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
