from urllib.parse import urlparse, urlunparse

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic import FormView, RedirectView, TemplateView, UpdateView, View

from accounts import forms
from accounts.backends import CLIPPER_SESSION_KEY, get_cas_client
from accounts.models import EmailUser
from accounts.tokens import email_token_generator
from site_settings.models import SiteSettings


def send_validation_email(request, user: EmailUser, subject: str, template: str) -> None:
    """Send a validation email to user"""
    current_site = get_current_site(request)
    message = render_to_string(
        template,
        {
            "user": user,
            "domain": current_site.domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": email_token_generator.make_token(user),
        },
    )
    user.email_user(subject, message)


class LoginView(auth_views.LoginView):
    """Vue pour se connecter"""

    template_name = "login.html"
    redirect_authenticated_user = True
    redirect_url = reverse_lazy("profile")
    form_class = forms.LoginForm


class LogoutView(RedirectView):
    """Vue pour se deconnecter"""

    permanent = False
    pattern_name = "home"

    clipper_connected: bool
    message = "Vous avez bien été déconnecté·e."

    def setup(self, request: HttpRequest) -> None:
        super().setup(request)
        if CLIPPER_SESSION_KEY in request.session:
            del request.session[CLIPPER_SESSION_KEY]
            self.clipper_connected = True
        else:
            self.clipper_connected = False

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            logout(self.request)
        next_page = super().get_redirect_url(*args, **kwargs)
        if self.clipper_connected:
            cas_client = get_cas_client(self.request)

            # If the next_url is local (no hostname), make it absolute so that the user
            # is correctly redirected from CAS.
            if next_page is not None and not urlparse(next_page).netloc:
                request = self.request
                next_page = urlunparse((request.scheme, request.get_host(), next_page, "", "", ""))

            next_page = cas_client.get_logout_url(redirect_url=next_page)
        messages.success(self.request, self.message)
        return next_page


# ==============================
# Create Account
# ==============================


class CreateAccountView(View):
    """Vue pour la creation de compte"""

    form_class = forms.CreateAccountForm
    template_name = "create_account.html"
    email_template = "email/activation.html"

    @staticmethod
    def check_creation_allowed() -> None:
        """Vérifie que la création de compte est authorisée
        Renvoie un 404 si ce n'est pas le cas"""
        settings = SiteSettings.load()
        if not settings.registrations_open:
            raise Http404("La création de compte n'est pas ouverte actuellement")

    def get(self, request, *args, **kwargs):
        """handle get requests"""
        self.check_creation_allowed()
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        """handle post requests"""
        self.check_creation_allowed()
        form = self.form_class(request.POST)
        if not form.is_valid():
            messages.error(
                request,
                "Formulaire invalide. Veuillez corriger les erreurs et le renvoyer.",
            )
            return render(request, self.template_name, {"form": form})

        user = form.save()
        user.is_active = False  # can't login until email validation
        user.email_confirmed = False
        user.save()

        send_validation_email(request, user, "Activer votre compte Interludes", self.email_template)

        messages.info(
            request,
            "Un lien vous a été envoyé par mail. Utilisez le pour finaliser la création de compte.",
        )

        return redirect("accounts:login")


class ActivateAccountView(RedirectView):
    """Vue d'activation de compte (lien envoyé par mail)"""

    permanent = False
    success_pattern_name = "profile"
    failure_pattern_name = "home"

    def get_redirect_url(self, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = EmailUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, EmailUser.DoesNotExist):
            messages.error(
                self.request,
                "Le lien de confirmation d'adresse mail ne correspond à aucun·e " "utilisateur·ice inscrit·e",
            )
            return reverse(self.failure_pattern_name)

        if not email_token_generator.check_token(user, token):
            messages.error(
                self.request,
                "Le lien de confirmation d'adresse mail est invalide ou déjà utilisé",
            )
            return reverse(self.failure_pattern_name)

        user.is_active = True
        user.email_confirmed = True
        user.save()
        login(self.request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request, "Votre adresse email a bien été confirmée.")
        return reverse(self.success_pattern_name)


# ==============================
# Update personal info
# ==============================


class UpdateAccountView(LoginRequiredMixin, UpdateView):
    """Vue pour la mise à jour des infos personnelles"""

    template_name = "update.html"
    form_class = forms.UpdateAccountForm
    email_template = "email/change.html"

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["update_form"] = context["form"]
        context["password_form"] = forms.UpdatePasswordForm(user=self.request.user)
        return context

    def get_success_url(self):
        assert isinstance(self.request.user, EmailUser)
        if not self.request.user.email_confirmed:
            send_validation_email(
                self.request,
                self.request.user,
                "Valider le changement d'email de votre compte Interludes",
                self.email_template,
            )

            messages.info(
                self.request,
                "Un lien vous a été envoyé par mail. Utilisez le pour valider la mise à jour.",
            )

            # return reverse("registration:email_confirmation_needed")
        return reverse("profile")

    def form_valid(self, form):
        messages.success(self.request, "Informations personnelles mises à jour")
        return super().form_valid(form)


class UpdatePasswordView(LoginRequiredMixin, FormView):
    """Change a user's password"""

    template_name = "update.html"
    form_class = forms.UpdatePasswordForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["password_form"] = context["form"]
        context["update_form"] = forms.UpdateAccountForm(instance=self.request.user)
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        assert isinstance(self.request.user, EmailUser)
        form.apply()
        messages.success(self.request, "Mot de passe mis à jour")
        login(self.request, self.request.user, backend="django.contrib.auth.backends.ModelBackend")
        return redirect("profile")


# ==============================
# Reset password
# ==============================


class ResetPasswordView(auth_views.PasswordResetView):
    """Vue pour le gestion du mot de passe oublié"""

    email_template_name = "email/password_reset.html"
    subject_template_name = "email/password_reset.txt"
    success_url = reverse_lazy("accounts:login")
    template_name = "password_reset.html"
    form_class = forms.PasswordResetEmailForm

    def form_valid(self, form):
        messages.info(self.request, "Un email vous a été envoyé avec un lien de réinitialisation")
        return super().form_valid(form)


class ResetPasswordConfirmView(auth_views.PasswordResetConfirmView):
    """Vue demandant de saisir un nouveau mot de passe"""

    success_url = reverse_lazy("accounts:login")
    template_name = "password_reset_confirm.html"

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été enregistré")
        return super().form_valid(form)


# ==============================
# Delete account
# ==============================


class DeleteConfirmView(LoginRequiredMixin, TemplateView):
    template_name = "delete_account.html"


class DeleteFinalView(LogoutView):
    pattern_name = "home"
    message = "Votre compte a été supprimé"

    def get_redirect_url(self, *args, **kwargs):
        self.user = self.request.user
        next_page = super().get_redirect_url(*args, **kwargs)
        self.user.delete()
        return next_page


# ==============================
# Clipper
# ==============================


class ClipperLoginView(View):
    """CAS authentication view.

    Implement the CAS authentication scheme:

    1. We first redirect the user to the student CAS.
    2. The user comes back with a ticket, we validate it to make sure the user is legit
       (validation is delegated to the ENSCASBackend).
    3. We redirect the user to the next page.
    """

    http_method_names = ["get"]

    def get_next_url(self) -> str:
        """Decide where to go after a successful login.

        Look for (in order):
        - a `next` GET parameter;
        - a `CASNEXT` session variable;
        - the `LOGIN_REDIRECT_URL` django setting.
        """
        request = self.request
        next_url = request.GET.get("next")
        if next_url is None and "CASNEXT" in request.session:
            next_url = request.session["CASNEXT"]
            del request.session["CASNEXT"]
        if next_url is None:
            next_url = reverse("profile")
        return str(next_url)

    def get(self, request: HttpRequest, *args, **kwargs):
        ticket = request.GET.get("ticket")

        if not ticket:
            request.session["CASNEXT"] = self.get_next_url()
            cas_client = get_cas_client(request)
            return redirect(cas_client.get_login_url())

        user = authenticate(request, ticket=ticket)
        if user is None:
            raise PermissionDenied("Connection échouée !")
        login(request, user, backend="")
        return redirect(self.get_next_url())
