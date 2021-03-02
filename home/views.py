from django.contrib.sitemaps import Sitemap
from django.shortcuts import redirect, render
from django.urls import reverse

from home.models import InterludesActivity

def static_view(request, template):
	"""Simple vues statique (rendu html)"""
	activities = InterludesActivity.objects.filter(display=True).order_by("title")
	return render(request, template, {'activities': activities})

class StaticViewSitemap(Sitemap):
	"""Vue générant la sitemap.xml du site"""
	changefreq = 'monthly'

	def items(self):
		return ["home", "inscription", "activites", "FAQ"]

	def location(self, item):
		return reverse(item)

	def priority(self, obj):
		# Priorize home page over the rest in search results
		if obj == "home" or obj == "":
				return 0.8
		else:
			return None # defaults to 0.5 when unset