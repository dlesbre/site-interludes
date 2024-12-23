from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("clipper/", views.ClipperLoginView.as_view(), name="clipper"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("create/", views.CreateAccountView.as_view(), name="create"),
    path("update/", views.UpdateAccountView.as_view(), name="update"),
    path("delete/", views.DeleteConfirmView.as_view(), name="delete"),
    path("delete/final", views.DeleteFinalView.as_view(), name="delete_final"),
    path("change_password/", views.UpdatePasswordView.as_view(), name="change_password"),
    path(
        "activate/<uidb64>/<token>/",
        views.ActivateAccountView.as_view(),
        name="activate",
    ),
    path("password_reset/", views.ResetPasswordView.as_view(), name="password_reset"),
    path(
        "password_reset/<uidb64>/<token>/",
        views.ResetPasswordConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]
