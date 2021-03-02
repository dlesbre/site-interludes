from django.urls import include, path
import django.contrib.auth.views as dj_auth_views

from accounts.views import create_account, logout_view

app_name = "accounts"

urlpatterns = [
	path("login/", dj_auth_views.LoginView.as_view(), name="login"),
	path("logout/", logout_view, name="logout"),
	path("create/", create_account, name="create")
]
