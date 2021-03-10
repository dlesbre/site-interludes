from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.urls import path, include

from home import views

sitemaps = {"static_pages": views.StaticViewSitemap}

urlpatterns = [
	path('', views.HomeView.as_view(), {"template": "home.html"}, name = 'home'),
	path('inscription/', views.RegisterView.as_view(), name = 'inscription'),
	path('desinscription/', views.UnregisterView.as_view(), name="desinscription"),
	path('activites/', views.ActivityView.as_view(), {"template":"activites.html"}, name = 'activites'),
	path('faq/', views.FAQView.as_view(), {"template":"faq.html"}, name = 'FAQ'),
	path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	path('metrics/', views.MetricsView.as_view(), name="metrics"),
	path(
		'sitemap.xml', sitemap, {'sitemaps': sitemaps},
		name='django.contrib.sitemaps.views.sitemap'
	),
	path('accounts/', include("accounts.urls")),
]
