from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe

from accounts.models import EmailUser
from shared.forms import FormRenderMixin

def password_criterions_html():
	"""Wraps password criterions into nice html used by other forms"""
	def wrap_str(s, tagopen, tagclose=None):
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


class CreateAccountForm(FormRenderMixin, UserCreationForm):
	"""Form used to register a new user"""
	class Meta:
		model = EmailUser
		fields = ('email', 'first_name', 'last_name', 'password1', 'password2',)


class UpdateAccountForm(FormRenderMixin, forms.ModelForm):
	"""Form used to update name/email"""
	class Meta:
		model = EmailUser
		fields = ('email', 'first_name', 'last_name')
		help_texts = {"email": "Si vous la changez, il faudra confirmer la nouvelle adresse",}

	@staticmethod
	def normalize_email(email):
		""" Returns a normalized email """
		return email.lower()

	def clean_email(self):
		""" Check email uniqueness """
		email = self.cleaned_data["email"]
		if email == self.instance.email:
				return email
		norm_email = self.normalize_email(email)
		if EmailUser.objects.filter(email=norm_email).count() > 0:
			raise forms.ValidationError(
					"Un autre compte avec cette adresse mail existe déjà."
			)
		return norm_email

	def save(self, *args, commit=True, **kwargs):
		email_changed = "email" in self.changed_data
		user = super().save(*args, commit=False, **kwargs)
		if email_changed:
			user.email_confirmed = False
			user.is_active = False
		if commit:
			user.save()
		return user

class UpdatePasswordForm(FormRenderMixin, forms.Form):
	""" Form to update one's password """

	current_password = forms.CharField(
		widget=forms.PasswordInput, label="Mot de passe actuel",
	)
	password = forms.CharField(
		widget=forms.PasswordInput,
		help_text=password_criterions_html(),
		label="Nouveau mot de passe",
	)
	password_confirm = forms.CharField(
		widget=forms.PasswordInput, label="Nouveau mot de passe (confirmation)",
	)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop("user", None)
		super().__init__(*args, **kwargs)

	def clean_current_password(self):
		""" Check current password correctness """
		cur_password = self.cleaned_data["current_password"]
		if authenticate(username=self.user.email, password=cur_password) != self.user:
				raise forms.ValidationError("Votre mot de passe actuel est incorrect.")
		return cur_password

	def clean_password(self):
		""" Check password strength """
		password = self.cleaned_data["password"]
		password_validation.validate_password(password)
		return password

	def clean_password_confirm(self):
		""" Check that both passwords match """
		cleaned_data = super().clean()
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
		""" Apply the password change, assuming validation was already passed """
		self.user.set_password(self.cleaned_data["password"])
		self.user.save()
