from django.urls import path

from .views import HTMLPageView

urlpatterns = [
	path("", HTMLPageView.as_view(), {"slug": ""}, name="home"),
	path("<slug:slug>/", HTMLPageView.as_view(), name="html_page"),
]
