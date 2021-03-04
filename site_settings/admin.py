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
	list_display = ("contact_email", "date_start", "date_end", "registrations_open", "inscriptions_open",)
	list_display_links = None
	list_editable = ("contact_email", "date_start", "date_end", "registrations_open", "inscriptions_open",)
