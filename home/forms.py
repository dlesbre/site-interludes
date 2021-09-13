from django import forms
from django.core.exceptions import ValidationError

from home import models
from shared.forms import FormRenderMixin


class InscriptionForm(FormRenderMixin, forms.ModelForm):

	class Meta:
		model = models.ParticipantModel
		fields = (
			"school", "sleeps", # "mug",
			"meal_friday_evening", "meal_saturday_morning", "meal_saturday_midday",
			"meal_saturday_evening", "meal_sunday_morning", "meal_sunday_midday",
		)

	field_groups = [["school"], ["sleeps"], #["mug"],
		[
			"meal_friday_evening", "meal_saturday_morning", "meal_saturday_midday",
			"meal_saturday_evening", "meal_sunday_morning", "meal_sunday_midday",
		]
	]

	def save(self, *args, commit=True, **kwargs):
		participant = super().save(*args, commit=False, **kwargs)
		participant.is_registered = True
		if commit:
			participant.save()
		return participant

class ActivityForm(FormRenderMixin, forms.ModelForm):
	class Meta:
		model = models.ActivityChoicesModel
		fields = ("slot",)
		labels = {"slot":""}

	def __init__(self, *args, **kwargs):
		super(ActivityForm, self).__init__(*args, **kwargs)
		slots = models.SlotModel.objects.filter(subscribing_open=True)
		self.fields['slot'].queryset = slots

class BaseActivityFormSet(forms.BaseFormSet):
	"""Form set that fails if duplicate activities"""
	def clean(self):
		"""Checks for duplicate activities"""
		if any(self.errors):
			# Don't bother validating the formset unless each form is valid on its own
			return
		activities = []
		for form in self.forms:
			if self.can_delete and self._should_delete_form(form):
				continue
			activity = form.cleaned_data.get('slot')
			if activity is None:
				continue
			if activity in activities:
				raise ValidationError("Vous ne pouvez pas sélectionner une même activtté plusieurs fois")
			activities.append(activity)


class ActivitySubmissionForm(FormRenderMixin, forms.ModelForm):

	class Meta:
		model = models.ActivityModel
		fields = (
			"title", "act_type", "game_type", "description",

			"host_info",

			"must_subscribe", "communicate_participants",
			"max_participants",	"min_participants",

			"duration", "desired_slot_nb",
			"available_friday_evening",
			"available_friday_night",
			"available_saturday_morning",
			"available_saturday_afternoon",
			"available_saturday_evening",
			"available_saturday_night",
			"available_sunday_morning",
			"available_sunday_afternoon",
			"constraints",

			"status", "needs",

			"comments",
		)

	def clean(self):
		cleaned_data = super().clean()
		maxi = cleaned_data.get("max_participants")
		mini = cleaned_data.get("min_participants")
		if maxi != 0 and mini > maxi:
			raise forms.ValidationError(
				"Le nombre minimal de participants est supérieur au nombre maximal",
				code="invalid_order"
			)
		return cleaned_data

	def save(self, user, *args, commit=True, **kwargs):
		"""Enregistre l'activité dans la base de données"""
		activity = models.ActivityModel(
			**self.cleaned_data,
			host=user, host_email=user.email,
			host_name=(user.first_name + user.last_name)
		)
		if commit:
			activity.save()
		return activity
