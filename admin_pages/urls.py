from django.urls import path, include

from admin_pages import views

urlpatterns = [
	path('', views.AdminView.as_view(), name="index"),
	path('export/activities/', views.ExportActivities.as_view(), name="activities.csv"),
	path('export/slots/', views.ExportSlots.as_view(), name="slots.csv"),
	path('export/participants/', views.ExportParticipants.as_view(), name="participants.csv"),
	path('export/activity_choices/', views.ExportActivityChoices.as_view(), name="activity_choices.csv"),
	path('email/send_user_emails_0564946523/', views.SendUserEmail.as_view(), name="email_users"),
	path('email/send_orga_emails_5682480453/', views.SendOrgaEmail.as_view(), name="email_orgas"),
	path('email/new_email/', views.NewEmail.as_view(), name="email_new"),
]
