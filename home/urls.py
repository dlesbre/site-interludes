from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.urls import path, include

from home import views

sitemaps = {"static_pages": views.StaticViewSitemap}

urlpatterns = [
	path('', views.static_view, {"template": "home.html"}, name = 'home'),
	path('inscription/', views.sign_up, name = 'inscription'),
	path('activites/', views.static_view, {"template":"activites.html"}, name = 'activites'),
	path('faq/', views.static_view, {"template":"faq.html"}, name = 'FAQ'),
	path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	path(
		'sitemap.xml', sitemap, {'sitemaps': sitemaps},
		name='django.contrib.sitemaps.views.sitemap'
	),
	path('accounts/', include("accounts.urls")),
]
