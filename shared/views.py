import csv

from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import View
from django.http import HttpResponse

class SuperuserRequiredMixin(UserPassesTestMixin):
	"""Classe restreignant l'accès d'une vue aux superusers"""
	raise_exception = True
	permission_denied_message = "Seul les superutilisateurs ont accès à cette page"

	def test_func(self):
		user = self.request.user
		return user.is_authenticated and user.is_superuser


class CSVWriteView(View):
	filename = "csv_file.csv"
	headers = None
	model = None
	exclude_fields = []
	fields = None

	def get_filename(self):
		return self.filename

	def get_headers(self):
		"""overload this to dynamicaly generate headers"""
		if self.headers:
			return self.headers
		if self.model:
			return self.get_field_names()
		return None

	def get_values(self):
		"""overload to change queryset used in self.get_rows"""
		if self.model:
			return self.model.objects.values()
		raise NotImplementedError("{}.get_values() isn't implemented when model is None".format(
			self.__class__.__name__
		))

	def get_field_names(self):
		"""overload to limit/change field names
		default to:
		- the value of self.field if not None
		- all fields minus those in exclude_fields otherwise"""
		if self.fields is not None:
			return self.fields
		return [
			field.name for field in self.model._meta.get_fields()
			if not field.name in self.exclude_fields
		]

	def get_rows(self):
		"""overload this to return the list of rows"""
		queryset = self.get_values()
		fields = self.get_field_names()
		table = []
		for row in queryset:
			table.append([row[field] for field in fields])
		return table

	def get(self, request, *args, **kwargs):
		response = HttpResponse(content_type='text/csv')
		filename = self.get_filename()
		if not filename.endswith(".csv"):
			filename += ".csv"
		response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

		writer = csv.writer(response)
		headers = self.get_headers()
		if headers is not None:
			writer.writerow(headers)

		for row in self.get_rows():
			writer.writerow(row)
		return response
