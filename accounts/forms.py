from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.safestring import mark_safe

from accounts.models import EmailUser


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
		if commit:
			user.save()
		return user
