from typing import List, Optional, TypeVar, Generic
from shared.views import CSVWriteView
from django.http import HttpRequest, HttpResponse

class CSVWriteViewForAdmin(CSVWriteView):
	def get_values(self):
		return self.queryset.values()

T = TypeVar("T")

class ExportCsvMixin(Generic[T]):
	"""
	class abstraite pour permettre l'export CSV rapide d'un modele
	utiliser csv_export_exclude pour exclure des colonnes du fichier généré
	"""
	filename : Optional[str] = None
	model : T

	csv_export_exclude : List[str] = []
	csv_export_fields = None

	def get_filename(self) -> str:
		if self.filename is not None:
			return self.filename
		return str(self.model._meta) # type: ignore

	def export_as_csv(self, request: HttpRequest, queryset) -> HttpResponse:
		"""renvoie un fichier CSV contenant l'information du queryset"""
		view = CSVWriteViewForAdmin(
			request=request, queryset=queryset, model=self.model,
			filename=self.get_filename(), exclude_fields=self.csv_export_exclude,
			fields=self.csv_export_fields,
		)
		return view.get(request)

	export_as_csv.short_description = "Exporter au format CSV" # type: ignore
	actions = ["export_as_csv"]
