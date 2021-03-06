import csv

from django.http import HttpResponse

class ExportCsvMixin:
	"""
	class abstraite pour permettre l'export CSV rapide d'un modele
	utiliser csv_export_exclude pour exclure des colonnes du fichier généré
	"""
	def export_as_csv(self, request, queryset):
		"""renvoie un fichier CSV contenant l'information du queryset"""
		meta = self.model._meta
		field_names = [field.name for field in meta.fields]

		if self.csv_export_exclude:
			field_names = [field for field in field_names if not field in self.csv_export_exclude]

		response = HttpResponse(content_type='text/csv')
		response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
		writer = csv.writer(response)

		writer.writerow(field_names)
		for obj in queryset:
			writer.writerow([getattr(obj, field) for field in field_names])

		return response

	export_as_csv.short_description = "Exporter au format CSV"

	actions = ["export_as_csv"]
	csv_export_exclude = None
