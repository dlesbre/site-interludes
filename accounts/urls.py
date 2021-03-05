from django.urls import include, path

from accounts.views import ActivateAccountView, CreateAccountView, LogoutView, LoginView

app_name = "accounts"

urlpatterns = [
	path("login/", LoginView.as_view(), name="login"),
	path("logout/", LogoutView.as_view(), name="logout"),
	path("create/", CreateAccountView.as_view(), name="create"),
	path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
]
