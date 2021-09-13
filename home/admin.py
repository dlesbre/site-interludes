from django.contrib import admin

from home import models
from shared.admin import ExportCsvMixin

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site 48h des Jeux"
# Tag html <title>
admin.site.site_title = "Admin 48h des jeux"


@admin.register(models.ActivityModel)
class ActivityModelAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des activités dans la vue django admin"""
	filename = "export_activites.csv"
	list_display = ("title", "host_name", "display", "must_subscribe",)
	list_filter = ("display", "must_subscribe", "status",)
	ordering = ("title", "host_name",)
	list_editable = ("display",)
	fields = (
		"title", "display",
		("host_name", "host_email"),
		"host_info",
		"act_type", "game_type",
		"description", "desc_as_html",
		("min_participants", "max_participants"),
		"must_subscribe",
		"communicate_participants",
		("duration", "desired_slot_nb"),
		(
			"available_friday_evening",
			"available_friday_night",
			"available_saturday_morning",
			"available_saturday_afternoon",
			"available_saturday_evening",
			"available_saturday_night",
			"available_sunday_morning",
			"available_sunday_afternoon"
		),
		"constraints",
		"status", "needs",
		"comments",
	)
	list_per_page = 100
	csv_export_fields = [
		# The key is "host_id" but listed as "host" in auto-found field names
		# which leads to an error...
		'id', 'display', 'title', 'act_type', 'game_type', 'description',
		'desc_as_html', 'host_id', 'host_name', 'host_email', 'host_info',
		'must_subscribe', 'communicate_participants', 'max_participants',
		'min_participants', 'duration', 'desired_slot_nb',
		'available_friday_evening', 'available_friday_night',
		'available_saturday_morning', 'available_saturday_afternoon',
		'available_saturday_evening', 'available_saturday_night',
		'available_sunday_morning', 'available_sunday_afternoon',
		'constraints', 'status', 'needs', 'comments'
	]


@admin.register(models.SlotModel)
class SlotModelAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des créneaux dans la vue d'admin"""
	filename = "export_slots.csv"
	list_display = ("__str__", "start", "room", "subscribing_open", "on_planning",)
	list_filter = ("subscribing_open", "on_planning", "activity__display",)
	list_editable = ("subscribing_open", "on_planning",)
	ordering = ("activity", "title", "start",)


@admin.register(models.ParticipantModel)
class ParticipantModelAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des participant dans la vue django admin"""
	filename = "export_participants.csv"
	list_display = ("user", "school", "is_registered")
	list_filter = (
		"school", "is_registered", "sleeps",
		"meal_friday_evening", "meal_saturday_morning", "meal_saturday_midday",
		"meal_saturday_evening", "meal_sunday_morning", "meal_sunday_midday",
	)
	ordering = ("user",)
	list_per_page = 200


@admin.register(models.ActivityChoicesModel)
class ActivityListAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des choix d'activités dans la vue django admin"""
	filename = "export_choix_activite.csv"
	list_display = ("slot", "participant", "priority", "accepted")
	list_filter = (
		"slot__activity", "participant__is_registered", "slot__activity__display",
		"accepted", "slot__subscribing_open",
	)
	list_editable = ("accepted",)
	ordering = ("slot", "priority", "participant",)
	list_per_page = 400
