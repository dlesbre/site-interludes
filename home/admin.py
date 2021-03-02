import csv
from django.contrib import admin
from django.http import HttpResponse

from home.models import InterludesActivity, InterludesParticipant, ActivityList

# Titre de la vue (objet <h1> dans le html)
admin.site.site_header = "Administration site interludes"

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

	actions = ["export_as_csv"]


@admin.register(InterludesActivity)
class InterludesActivityAdmin(admin.ModelAdmin, ExportCsvMixin):
	"""option d'affichage des activités dans la vue django admin"""
	list_display = ("title", "host_name", "display", "must_subscribe",)
	list_filter = ("display", "must_subscribe",)
	ordering = ("title", "host_name",)
	list_editable = ("display",)
	list_per_page = 100

@admin.register(InterludesParticipant)
class InterludesParticipantAdmin(admin.ModelAdmin, ExportCsvMixin):
	"""option d'affichage des participant dans la vue django admin"""
	list_display = ("name", "school",)
	list_filter = ("school",)
	ordering = ("name",)
	list_per_page = 200

@admin.register(ActivityList)
class ActivityListAdmin(admin.ModelAdmin, ExportCsvMixin):
	"""option d'affichage des choix d'activités dans la vue django admin"""
	list_display = ("participant", "priority", "activity",)
	list_filter = ("activity", "participant",)
	ordering = ("participant", "priority",)
	list_per_page = 200
