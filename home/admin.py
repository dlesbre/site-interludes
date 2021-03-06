import csv
from django.contrib import admin
from django.http import HttpResponse

from home.models import InterludesActivity, InterludesParticipant, ActivityList

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site interludes"
# Tag html <title>
admin.site.site_title = "Admin Interludes"

class ExportCsvMixin:
	"""class abstraite pour permettre l'export CSV rapide d'un modele"""
	def export_as_csv(self, request, queryset):
		"""renvoie un fichier CSV contenant l'information du queryset"""
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]

		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = "Exporter au format CSV"


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
