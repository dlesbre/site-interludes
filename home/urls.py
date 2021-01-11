from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.urls import path, include
from . import views

sitemaps = {"static_pages": views.StaticViewSitemap}

urlpatterns = [
	path('', views.static_view, {"slug":"home"}, name = 'home'),
	path('inscription/', views.static_view, {"slug":"inscription"}, name = 'inscription'),
	path('activites/', views.static_view, {"slug":"activites"}, name = 'activites'),
	path('faq/', views.static_view, {"slug":"faq"}, name = 'FAQ'),
	path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	path(
		'sitemap.xml', sitemap, {'sitemaps': sitemaps},
		name='django.contrib.sitemaps.views.sitemap'
	),
	path('accounts/', include("accounts.urls")),
]
