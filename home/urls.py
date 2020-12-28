from django.urls import path
from . import views

urlpatterns = [
	path('', views.static_view, {"slug":"home"}, name = 'home'),
]