from django.contrib import admin

from home.models import InterludesActivity, InterludesParticipant, ActivityList
from shared.admin import ExportCsvMixin

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site interludes"
# Tag html <title>
admin.site.site_title = "Admin Interludes"


@admin.register(InterludesActivity)
class InterludesActivityAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des activités dans la vue django admin"""
	list_display = ("title", "host_name", "display", "must_subscribe","on_planning")
	list_filter = ("display", "must_subscribe", "on_planning", "status")
	ordering = ("title", "host_name",)
	list_editable = ("display",)
	fields = (
		"title",
		("host_name", "host_email"),
		"status", "act_type", "duration",
		("min_participants", "max_participants"),
		"must_subscribe",
		"communicate_participants",
		"description",
		"display",
		"room", "start",
		"on_planning",
		"notes"
	)
	list_per_page = 100

@admin.register(InterludesParticipant)
class InterludesParticipantAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des participant dans la vue django admin"""
	list_display = ("user", "school", "is_registered")
	list_filter = (
		"school", "is_registered", "sleeps",
		"meal_friday_evening", "meal_saturday_morning", "meal_saturday_midday",
		"meal_saturday_evening", "meal_sunday_morning", "meal_sunday_midday",
	)
	ordering = ("user",)
	list_per_page = 200

@admin.register(ActivityList)
class ActivityListAdmin(ExportCsvMixin, admin.ModelAdmin):
	"""option d'affichage des choix d'activités dans la vue django admin"""
	list_display = ("activity", "participant", "priority", "accepted")
	list_filter = (
		"activity", "participant__is_registered", "activity__display",
		"accepted", "activity__must_subscribe",
	)
	list_editable = ("accepted",)
	ordering = ("activity", "priority", "participant",)
	list_per_page = 400
