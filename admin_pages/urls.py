from django.urls import path

from admin_pages import views
from site_settings.models import ENS

urlpatterns = [
    path("", views.AdminView.as_view(), name="index"),
    path("info", views.SiteInfo.as_view(), name="info"),
    path("export/activities/", views.ExportActivities.as_view(), name="activities.csv"),
    path("export/slots/", views.ExportSlots.as_view(), name="slots.csv"),
    path(
        "export/participants/",
        views.ExportParticipants.as_view(),
        name="participants.csv",
    ),
    path(
        "export/participants/ulm",
        views.ExportParticipants.as_view(school=ENS.ENS_ULM),
        name="participants_ulm.csv",
    ),
    path(
        "export/participants/lyon",
        views.ExportParticipants.as_view(school=ENS.ENS_LYON),
        name="participants_lyon.csv",
    ),
    path(
        "export/participants/rennes",
        views.ExportParticipants.as_view(school=ENS.ENS_RENNES),
        name="participants_rennes.csv",
    ),
    path(
        "export/participants/saclay",
        views.ExportParticipants.as_view(school=ENS.ENS_CACHAN),
        name="participants_saclay.csv",
    ),
    path(
        "export/activity_choices/",
        views.ExportActivityChoices.as_view(),
        name="activity_choices.csv",
    ),
    path(
        "email/send_user_emails_0564946523/",
        views.SendUserEmail.as_view(),
        name="email_users",
    ),
    path(
        "email/send_orga_emails_5682480453/",
        views.SendOrgaEmail.as_view(),
        name="email_orgas",
    ),
    path("email/new_email/", views.NewEmail.as_view(), name="email_new"),
]
