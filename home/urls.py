from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.urls import path, include

from home import views

sitemaps = {"static_pages": views.StaticViewSitemap}

urlpatterns = [
	path('', views.HomeView.as_view(), name = 'home'),
	path('inscription/', views.RegisterView.as_view(), name = 'inscription'),
	path('desinscription/', views.UnregisterView.as_view(), name="desinscription"),
	path('activites/', views.ActivityView.as_view(), name = 'activites'),
	path('activites/nouvelle/', views.ActivitySubmissionView.as_view(), name = 'activity_submission'),
	path('faq/', views.FAQView.as_view(), name = 'FAQ'),
	path("profil/", views.ProfileView.as_view(), name="profile"),
	path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	path(
		'sitemap.xml', sitemap, {'sitemaps': sitemaps},
		name='django.contrib.sitemaps.views.sitemap'
	),
	path('admin_pages/', include(('admin_pages.urls', 'admin_pages'), namespace="admin_pages")),
	path('comptes/', include("accounts.urls")),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
