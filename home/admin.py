import csv
from django.contrib import admin
from django.http import HttpResponse

from home.models import InterludesActivity, InterludesParticipant, ActivityList
from shared.admin import ExportCsvMixin

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site interludes"
# Tag html <title>
admin.site.site_title = "Admin Interludes"


@admin.register(InterludesActivity)
class InterludesActivityAdmin(admin.ModelAdmin, ExportCsvMixin):
	"""option d'affichage des activités dans la vue django admin"""
	list_display = ("title", "host_name", "display", "must_subscribe","on_planning")
	list_filter = ("display", "must_subscribe", "on_planning")
	ordering = ("title", "host_name",)
	list_editable = ("display",)
	list_per_page = 100
	actions = ["export_as_csv"]

@admin.register(InterludesParticipant)
class InterludesParticipantAdmin(admin.ModelAdmin, ExportCsvMixin):
	"""option d'affichage des participant dans la vue django admin"""
	list_display = ("user", "school", "is_registered")
	list_filter = ("school", "is_registered")
	ordering = ("user",)
	list_per_page = 200
	actions = ["export_as_csv"]

@admin.register(ActivityList)
class ActivityListAdmin(admin.ModelAdmin, ExportCsvMixin):
	"""option d'affichage des choix d'activités dans la vue django admin"""
	list_display = ("participant", "priority", "activity",)
	list_filter = ("activity", "participant",)
	ordering = ("participant", "priority",)
	list_per_page = 200
	actions = ["export_as_csv"]
