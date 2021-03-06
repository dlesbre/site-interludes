from django import forms
from django.contrib.auth import authenticate, password_validation
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe

from accounts.models import EmailUser

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

class FormRenderMixin:
	""" A mixin that can be included in any form to make it render to html as we want
	it on this website.

	The following class variables can be adjusted to tweak display:

	* `tooltip_helptexts`: a list of fields whose helptexts, if any, should be rendered
	  as a question mark's tooltip instead of being inlined.
	* `field_groups`: if `None`, the fields will be rendered in order, as eg. `as_p`
	  would.
	  Else, can be set to any nested list structure, containing each field name exactly
	  once. The structure `[['a', 'b'], ['c']]` would then group together the fields a
	  and b, then group together the single field c.

	"""

	tooltip_helptexts = []
	field_groups = None

	class BadFieldGroups(Exception):
		pass

	def as_html(self):
		""" Render the form to html """

		def get_field_treelike():
			def map_to_field(treelike):
				if isinstance(treelike, str):
					if treelike in self.fields:
						return {
							"field": self[treelike],
							"tooltip": treelike in self.tooltip_helptexts,
						}
					raise self.BadFieldFroups
				return list(map(map_to_field, treelike))

			if self.field_groups is not None:
				return map_to_field(self.field_groups)
			else:
				return [
					list(
						map(
							lambda field: {
								"field": self[field],
								"tooltip": field in self.tooltip_helptexts,
							},
							self.fields,
						)
					)
				]

		def gen_html(treelike):
			def gen_node(subtree):
				if isinstance(subtree, list):
					return '<div class="fieldgroup">\n{}</div>'.format(
						gen_html(subtree)
					)
				else:  # Simple field
					inline_helptext_html = (
						(
							'    <span class="helptext inline_helptext">'
							"{inline_helptext}</span>\n"
						).format(inline_helptext=subtree["field"].help_text)
						if subtree["field"].help_text and not subtree["tooltip"]
						else ""
					)
					tooltip_html = (
						(
							'<span class="tooltip" tabindex="0">\n'
							'<i class="fa fa-question-circle" aria-hidden="true"></i>\n'
							'<span class="tooltiptext">\n'
							"  {tooltiphtml}\n"
							"</span>\n"
							"</span>"
						).format(tooltiphtml=subtree["field"].help_text)
						if subtree["field"].help_text and subtree["tooltip"]
						else ""
					)

					field_classes = "formfield"
					if subtree["field"].errors:
						field_classes += " error_field"

					labelled_input_classes = "labelled_input"
					if subtree["field"].field.widget.input_type in [
						"checkbox",
						"radio",
					]:
						labelled_input_classes += " checkbox_input"

					html = (
						'<div class="{field_classes}" id="formfield_{label_for}">\n'
						'  <div class="{labelled_input_classes}">\n'
						'    <div class="label_line">\n'
						'      <label for="{label_for}">{label_text}&nbsp;:</label>\n{errors}'
						"    </div>\n"
						"    {field_html}\n"
            '    <div class="help">{tooltip}{inline_helptext_html}</div>\n'
						"  </div>\n"
						"</div>"
					).format(
						field_classes=field_classes,
						labelled_input_classes=labelled_input_classes,
						errors=subtree["field"].errors or "",
						label_for=subtree["field"].id_for_label,
						label_text=subtree["field"].label,
						tooltip=tooltip_html,
						inline_helptext_html=inline_helptext_html,
						field_html=subtree["field"],
					)
					return html

			return "\n".join(map(gen_node, treelike))

		fields_html = gen_html(get_field_treelike())
		with_errors = "{form_errors}\n{fields}\n".format(
			form_errors=self.non_field_errors() if self.non_field_errors() else "",
			fields=fields_html,
		)
		return mark_safe(with_errors)

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
		email = self.cleaned_data["email"]
		email_changed = email != self.instance.username
		user = super().save(*args, commit=False, **kwargs)
		user.username = email
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
