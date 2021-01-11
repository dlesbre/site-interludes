from django.urls import include, path
import django.contrib.auth.views as dj_auth_views
from .views import logout 

app_name = "accounts"

accounts_patterns = [
    path("login/", dj_auth_views.LoginView.as_view(), name="login"),
    path("logout/", logout, name="logout"),
]

urlpatterns = [
        path("", include(accounts_patterns)),
]
