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
	path('faq/', views.FAQView.as_view(), name = 'FAQ'),
	path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	path('admin_site/', views.AdminView.as_view(), name="site_admin"),
	path('export/activities/', views.ExportActivities.as_view(), name="activities.csv"),
	path('export/participants/', views.ExportParticipants.as_view(), name="participants.csv"),
	path('export/activity_choices/', views.ExportActivityChoices.as_view(), name="activity_choices.csv"),
	path('email/send_user_emails_0564946523/', views.SendUserEmail.as_view(), name="email_users"),
	path('email/send_orga_emails_5682480453/', views.SendOrgaEmail.as_view(), name="email_orgas"),
	path(
		'sitemap.xml', sitemap, {'sitemaps': sitemaps},
		name='django.contrib.sitemaps.views.sitemap'
	),
	path('accounts/', include("accounts.urls")),
]
