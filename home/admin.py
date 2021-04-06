from django.contrib import admin

from home import models
from shared.admin import ExportCsvMixin

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site interludes"
# Tag html <title>
admin.site.site_title = "Admin Interludes"


@admin.register(models.InterludesActivity)
class InterludesActivityAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des activités dans la vue django admin"""
	filename = "export_activites.csv"
	list_display = ("title", "host_name", "display", "must_subscribe",)
	list_filter = ("display", "must_subscribe", "status",)
	ordering = ("title", "host_name",)
	list_editable = ("display",)
	fields = (
		"title",
		("host_name", "host_email"),
		"status", "act_type", "duration",
		("min_participants", "max_participants"),
		"must_subscribe",
		"communicate_participants",
		"description", "desc_as_html",
		"display",
		"notes",
	)
	list_per_page = 100


@admin.register(models.InterludesSlot)
class InterludesSlotAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des crénaux dans la vue d'admin"""
	filename = "export_slots.csv"
	list_display = ("__str__", "start", "room", "subscribing_open", "on_planning",)
	list_filter = ("subscribing_open", "on_planning", "activity__display",)
	list_editable = ("subscribing_open", "on_planning",)
	ordering = ("activity", "title", "start",)


@admin.register(models.InterludesParticipant)
class InterludesParticipantAdmin(ExportCsvMixin, admin.ModelAdmin):
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


@admin.register(models.InterludesActivityChoices)
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
