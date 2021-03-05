from django.urls import include, path
import django.contrib.auth.views as dj_auth_views

from accounts.views import logout_view, ActivateAccountView, CreateAccountView

app_name = "accounts"

urlpatterns = [
	path("login/", dj_auth_views.LoginView.as_view(), name="login"),
	path("logout/", logout_view, name="logout"),
	path("create/", CreateAccountView.as_view(), name="create"),
	path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
]
