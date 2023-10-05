from django import forms

from home import models
from shared.forms import FormRenderMixin


class ActivitySubmissionForm(FormRenderMixin, forms.ModelForm):
    class Meta:
        model = models.ActivityModel
        fields = (
            "title",
            "act_type",
            "game_type",
            "description",
            "host_name",
            "host_email",
            "host_info",
            "must_subscribe",
            "max_participants",
            "min_participants",
            "duration",
            "desired_slot_nb",
            "available_friday_evening",
            "available_friday_night",
            "available_saturday_morning",
            "available_saturday_afternoon",
            "available_saturday_evening",
            "available_saturday_night",
            "available_sunday_morning",
            "available_sunday_afternoon",
            "constraints",
            "needs",
            "comments",
        )

    def clean(self):
        cleaned_data = super().clean()
        maxi = cleaned_data.get("max_participants")
        mini = cleaned_data.get("min_participants")
        if maxi != 0 and mini > maxi:
            raise forms.ValidationError(
                "Le nombre minimal de participants est supérieur au nombre maximal",
                code="invalid_order",
            )
        return cleaned_data

    def save(self, *args, commit=True, **kwargs):
        """Enregistre l'activité dans la base de données"""
        activity = models.ActivityModel(
            **self.cleaned_data,
        )
        if commit:
            activity.save()
        return activity
