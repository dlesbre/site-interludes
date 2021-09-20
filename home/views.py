from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.forms import formset_factory
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, RedirectView, TemplateView, View

from authens.views import LogoutView as AuthensLogoutView

from home import models
from home.forms import ActivitySubmissionForm
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
	context['planning'] = models.SlotModel.objects.filter(on_planning=True).order_by("title")
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
		context['activities'] = models.ActivityModel.objects.filter(display=True).order_by("title")
		context.update(get_planning_context())
		return context


class FAQView(TemplateView):
	"""Vue pour la FAQ"""
	template_name = "faq.html"


class TableView(LoginRequiredMixin, RedirectView):
	url = reverse_lazy("home")

	def get(self, request, id=id, *args, **kwargs):
		contact = models.AdjacencyModel(
			time=timezone.now(), user=request.user, table=id
		)
		contact.save()
		messages.success(request, "Présence à la table {} enregistrée".format(id))
		return super().get(request, id=id, *args, **kwargs)

# ==============================
# Activity Submission Form
# ==============================


class ActivitySubmissionView(LoginRequiredMixin, FormView):
	"""Vue pour proposer une activité"""
	template_name = "activity_submission.html"
	form_class = ActivitySubmissionForm
	success_url = reverse_lazy("activites")

	@staticmethod
	def submission_check():
		"""Vérifie si le formulaire est ouvert ou non"""
		settings = SiteSettings.load()
		return settings.activity_submission_open

	def not_open(self, request):
		"""Appelé quand le formulaire est désactivé"""
		messages.error(request, "La soumission d'activité est desactivée")
		return redirect(self.success_url, permanent=False)

	def get_initial(self):
		init = super().get_initial()
		user = self.request.user
		init.update({"host_name": user.username, "host_email": user.email})
		return init

	def get(self, request, *args, **kwargs):
		if not self.submission_check():
			return self.not_open(request)
		return super().get(self, request, *args, **kwargs)

	def post(self, request, *args, **kwargs):
		if not self.submission_check():
			return self.not_open(request)
		form = self.form_class(request.POST)
		if not form.is_valid():
			context = self.get_context_data
			context["form"] = form
			return render(request, self.template_name, context)

		form.save()

		messages.success(request, "Votre activité a bien été enregistrée. Elle sera affichée sur le site après relecture par les admins.")
		return redirect(self.success_url, permanent=False)


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


class LogoutView(AuthensLogoutView):
	def get_next_page(self):
		messages.success(self.request, "Vous avez bien été déconnecté.")
		return reverse("home")
