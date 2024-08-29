from django import forms
from django.conf import settings
from django.db.models import TextChoices


class Recipients(TextChoices):
    ALL = ("a", "tous les utilisateurs")
    REGISTERED = ("b", "tous les inscrits")
    ULMITES = ("U", "tous les inscrits ulmites")
    LYONNAIS = ("L", "tous les inscrits lyonnais")
    RENNAIS = ("R", "tous les inscrits rennais")
    CACHANAIS = ("C", "tous les inscrits saclaysiens")
    ORGAS = ("o", "tous les organisateurs d'activités")


class SendEmailForm(forms.Form):
    """Formulaire pour un envoie d'email
    à tous les utilisateurs/inscrits"""

    dest = forms.ChoiceField(
        choices=Recipients.choices,
        required=True,
        label="Envoyer à",
        initial=Recipients.REGISTERED,
    )
    subject = forms.CharField(
        max_length=100,
        required=True,
        label="Sujet",
        initial=settings.USER_EMAIL_SUBJECT_PREFIX,
        strip=True,
    )
    text = forms.CharField(label="Contenu", strip=True, widget=forms.Textarea)
