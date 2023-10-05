from typing import List, Optional

from shared.views import CSVWriteView


class CSVWriteViewForAdmin(CSVWriteView):
    def get_values(self):
        return self.queryset.values()


class ExportCsvMixin:
    """
    class abstraite pour permettre l'export CSV rapide d'un modele
    utiliser csv_export_exclude pour exclure des colonnes du fichier généré
    """

    filename: Optional[str] = None

    csv_export_exclude = []
    csv_export_fields: Optional[List[str]] = None

    def get_filename(self):
        if self.filename:
            return self.filename
        return str(self.model._meta)

    def export_as_csv(self, request, queryset):
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
