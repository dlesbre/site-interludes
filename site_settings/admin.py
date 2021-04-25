from django.contrib import admin

from site_settings.models import SiteSettings

class SingletonModelAdmin(admin.ModelAdmin):
	"""Prevent deletion or adding rows"""
	actions = None

	def has_add_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return False

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):

	def planning_file_link(self, obj):
		if obj.file:
			return "<a href='%s'>download</a>" % (obj.file.url,)
		else:
			return "No attachment"
