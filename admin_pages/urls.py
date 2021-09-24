from django.urls import path, include

from admin_pages import views

urlpatterns = [
	path('', views.AdminView.as_view(), name="index"),
	path('export/activities/', views.ExportActivities.as_view(), name="activities.csv"),
	path('export/slots/', views.ExportSlots.as_view(), name="slots.csv"),
	path('export/presences/', views.ExportAdjacencies.as_view(), name="presences.csv"),
	path('email/', views.NewEmail.as_view(), name="email_new"),
]
