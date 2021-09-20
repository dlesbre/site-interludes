from django import forms
from django.conf import settings


class SendEmailForm(forms.Form):
	"""Formulaire pour un envoie d'email
	à tous les utilisateurs"""

	subject = forms.CharField(
		max_length=100, required=True,
		label="Sujet", initial=settings.USER_EMAIL_SUBJECT_PREFIX,
		strip=True
	)
	text = forms.CharField(
		label="Contenu", strip=True, widget=forms.Textarea
	)
