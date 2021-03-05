from django.contrib.sitemaps import Sitemap
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import TemplateView

from home.models import InterludesActivity


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


def sign_up(request):
	"""Page d'inscription"""
	if not settings.REGISTRATION_EVENT_INSCRIPTIONS_OPEN:
		return static_view(request, "inscription/closed.html")
	if not request.user.is_authenticated:
		return static_view(request, "inscription/signin.html")
	# TODO : actual inscription form


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
