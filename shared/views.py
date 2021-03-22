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



	def get_headers(self):
		"""overload this to dynamicaly generate headers"""
		if self.headers:
			return self.headers
		if self.model:
			return [field.name for field in self.model._meta.fields]
		return None

	def get_rows(self):
		"""overload this to return the list of rows"""
		if self.model:
			queryset = self.model.objects.values()
			fields = self.model._meta.fields
			table = []
			for row in queryset:
				table.append([row[field.name] for field in fields])
			return table
		raise NotImplementedError("{}.get_rows isn't implemented".format(self.__class__.__name__))

	def get(self, request, *args, **kwargs):
		response = HttpResponse(content_type='text/csv')
		filename = self.filename
		if not filename.endswith(".csv"):
			filename += ".csv"
		response['Content-Disposition'] = 'attachment; filename="{}"'.format(self.filename)

		writer = csv.writer(response)
		headers = self.get_headers()
		if headers is not None:
			writer.writerow(headers)

		for row in self.get_rows():
			writer.writerow(row)
		print(writer)
		return response
