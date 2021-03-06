from django.urls import include, path

from accounts import views

app_name = "accounts"

urlpatterns = [
	path("login/", views.LoginView.as_view(), name="login"),
	path("logout/", views.LogoutView.as_view(), name="logout"),
	path("profile/", views.ProfileView.as_view(), name="profile"),
	path("create/", views.CreateAccountView.as_view(), name="create"),
	path("update/", views.UpdateAccountView.as_view(), name="update"),
	path("change_password/", views.UpdatePasswordView.as_view(), name="change_password"),
	path('activate/<uidb64>/<token>/', views.ActivateAccountView.as_view(), name='activate'),
]
