from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.shortcuts import redirect, render
from django.urls import reverse

from home.models import InterludesActivity

def static_view(request, template):
	"""Simple vues statique (rendu html)"""
	activities = InterludesActivity.objects.filter(display=True).order_by("title")
	return render(request, template, {'activities': activities})

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
