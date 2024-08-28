from django.urls import path

from admin_pages import views

urlpatterns = [
    path("", views.AdminView.as_view(), name="index"),
    path("export/activities/", views.ExportActivities.as_view(), name="activities.csv"),
    path("export/slots/", views.ExportSlots.as_view(), name="slots.csv"),
    path("email/", views.NewEmail.as_view(), name="email_new"),
    path("info", views.SiteInfo.as_view(), name="info"),
]
