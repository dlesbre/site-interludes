from typing import Generic, List, Optional, TypeVar

from django.contrib.admin import ModelAdmin
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse

from shared.views import CSVWriteView

T = TypeVar("T", bound=Model)


class CSVWriteViewForAdmin(CSVWriteView, Generic[T]):
    queryset: QuerySet[T]

    def get_values(self):
        return self.queryset.values()


class ExportCsvMixin(ModelAdmin, Generic[T]):
    """
    class abstraite pour permettre l'export CSV rapide d'un modele
    utiliser csv_export_exclude pour exclure des colonnes du fichier généré
    """

    filename: Optional[str] = None

    csv_export_exclude = []
    csv_export_fields: Optional[List[str]] = None

    def get_filename(self) -> str:
        if self.filename:
            return self.filename
        return str(self.model._meta)

    def export_as_csv(self, request: HttpRequest, queryset: QuerySet[T]) -> HttpResponse:
        """renvoie un fichier CSV contenant l'information du queryset"""
        view = CSVWriteViewForAdmin(
            request=request,
            queryset=queryset,
            model=self.model,
            filename=self.get_filename(),
            exclude_fields=self.csv_export_exclude,
            fields=self.csv_export_fields,
        )
        return view.get(request)

    export_as_csv.short_description = "Exporter au format CSV"
    actions = ["export_as_csv"]
