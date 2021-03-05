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
	pass