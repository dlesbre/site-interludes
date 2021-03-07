from django import forms

from home.models import ActivityList, InterludesParticipant
from shared.forms import FormRenderMixin


class InscriptionForm(FormRenderMixin, forms.ModelForm):

	class Meta:
		model = InterludesParticipant
		fields = (
			"school", "sleeps", "mug",
			"meal_friday_evening", "meal_saturday_morning", "meal_saturday_midday",
			"meal_saturday_evening", "meal_sunday_morning", "meal_sunday_midday",
		)

	field_groups = [["school"], ["sleeps"], ["mug"], [
		"meal_friday_evening", "meal_saturday_morning", "meal_saturday_midday",
		"meal_saturday_evening", "meal_sunday_morning", "meal_sunday_midday",
	]]

	def save(self, *args, commit=True, **kwargs):
		participant = super().save(*args, commit=False, **kwargs)
		participant.is_registered = True
		if commit:
			participant.save()
		return participant

class ActivityForm(FormRenderMixin, forms.ModelForm):
	class Meta:
		model = ActivityList
		fields = ("activity",)
