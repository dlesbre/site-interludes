from typing import Any, Optional

from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    UserCreationForm,
)
from django.utils.safestring import mark_safe

from accounts.models import EmailUser
from shared.forms import FormRenderMixin
from shared.models import normalize_email


def password_criterions_html() -> str:
    """Wraps password criterions into nice html used by other forms"""

    def wrap_str(s, tagopen: str, tagclose: Optional[str] = None) -> str:
        if not tagclose:
            tagclose = tagopen
        return "<{}>{}</{}>".format(tagopen, s, tagclose)

    criterions = password_validation.password_validators_help_texts()
    criterions_html = wrap_str(
        "\n".join(map(lambda crit: wrap_str(crit, "li"), criterions)),
        'ul class="helptext"',
        "ul",
    )
    return mark_safe(criterions_html)


class LoginForm(AuthenticationForm):
    """Form used when loging in"""

    def clean(self, *args, **kwargs):
        self.cleaned_data["username"] = normalize_email(self.cleaned_data.get("username"))  # type: ignore
        return super().clean(*args, **kwargs)


class CreateAccountForm(FormRenderMixin, UserCreationForm):
    """Form used to register a new user"""

    class Meta:
        model = EmailUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )


class UpdateAccountForm(FormRenderMixin, forms.ModelForm):
    """Form used to update name/email"""

    class Meta:
        model = EmailUser
        fields = ("email", "first_name", "last_name")
        help_texts = {
            "email": "Si vous la changez, il faudra confirmer la nouvelle adresse",
        }

    def clean_email(self) -> str:
        """Check email uniqueness"""
        email = self.cleaned_data["email"]
        if email == self.instance.email:
            return email  # type: ignore
        norm_email = normalize_email(email)
        if EmailUser.objects.filter(email=norm_email).count() > 0:
            raise forms.ValidationError(
                "Un autre compte avec cette adresse mail existe déjà."
            )
        return norm_email

    def save(self, commit=True) -> Any:
        email_changed = "email" in self.changed_data
        user = super().save(commit=False)
        if email_changed:
            user.email_confirmed = False
            user.is_active = False
        if commit:
            user.save()
        return user


class UpdatePasswordForm(FormRenderMixin, forms.Form):
    """Form to update one's password"""

    current_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Mot de passe actuel",
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text=password_criterions_html(),
        label="Nouveau mot de passe",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Nouveau mot de passe (confirmation)",
    )

    def __init__(self, *args, **kwargs) -> None:
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """Check current password correctness"""
        cur_password = self.cleaned_data["current_password"]
        if authenticate(username=self.user.email, password=cur_password) != self.user:
            raise forms.ValidationError("Votre mot de passe actuel est incorrect.")
        return cur_password

    def clean_password(self):
        """Check password strength"""
        password = self.cleaned_data["password"]
        password_validation.validate_password(password)
        return password

    def clean_password_confirm(self):
        """Check that both passwords match"""
        cleaned_data = super().clean()
        if not cleaned_data:
            return
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if not password:
            return None
        if password != password_confirm:
            raise forms.ValidationError(
                "Les deux mots de passe ne sont pas identiques."
            )
        return cleaned_data

    def apply(self):
        """Apply the password change, assuming validation was already passed"""
        self.user.set_password(self.cleaned_data["password"])
        self.user.save()


class PasswordResetEmailForm(PasswordResetForm):
    """Form used when asking email to send password reset linkk"""

    def clean(self, *args, **kwargs):
        self.cleaned_data["email"] = normalize_email(self.cleaned_data.get("email"))  # type: ignore
        return super().clean(*args, **kwargs)
