import csv
from typing import Generic, List, Optional, Type, TypeVar

from django.contrib.auth.mixins import UserPassesTestMixin
from django.db.models import Model, QuerySet
from django.http import HttpRequest, HttpResponse
from django.views import View


class SuperuserRequiredMixin(UserPassesTestMixin):
    """Classe restreignant l'accès d'une vue aux superusers"""

    raise_exception = True
    permission_denied_message = "Seul les superutilisateurs ont accès à cette page"

    def test_func(self):
        user = self.request.user  # type: ignore
        return user.is_authenticated and user.is_superuser


M = TypeVar("M", bound=Model)


class CSVWriteView(View, Generic[M]):
    filename = "csv_file.csv"
    headers: Optional[List[str]] = None
    model: Type[M]
    exclude_fields: List[str] = []
    fields: Optional[List[str]] = None

    def get_filename(self) -> str:
        return self.filename

    def get_headers(self) -> Optional[List[str]]:
        """overload this to dynamicaly generate column headers"""
        if self.headers:
            return self.headers
        if self.model:
            return self.get_field_names()
        return None

    def get_values(self) -> QuerySet[M]:
        """overload to change queryset used in self.get_rows"""
        if self.model:
            return self.model.objects.all()
        raise NotImplementedError(
            "{}.get_values() isn't implemented when model is None".format(
                self.__class__.__name__
            )
        )

    def get_field_names(self) -> List[str]:
        """overload to limit/change field names
        default to:
        - the value of self.field if not None
        - all fields minus those in exclude_fields otherwise"""
        if self.fields is not None:
            return self.fields
        return [
            field.name
            for field in self.model._meta.get_fields()
            if not field.name in self.exclude_fields
        ]

    def get_rows(self) -> List[List[str]]:
        """overload this to return the list of rows"""
        queryset = self.get_values()
        fields = self.get_field_names()
        table = []
        for row in queryset.values():
            table.append([row[field] for field in fields])
        return table

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        response = HttpResponse(content_type="text/csv")
        filename = self.get_filename()
        if not filename.endswith(".csv"):
            filename += ".csv"
        response["Content-Disposition"] = 'attachment; filename="{}"'.format(
            self.filename
        )

        writer = csv.writer(response)
        headers = self.get_headers()
        if headers is not None:
            writer.writerow(headers)

        for row in self.get_rows():
            writer.writerow(row)
        return response
