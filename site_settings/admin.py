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

	fieldsets = [
		(
			"Informations générales",
			{
				"fields": [
					# "hosting_school",
					"contact_email",
					("date_start", "date_end"),
					"affiche",
				]
			},
		),
		(
			"Activités",
			{
				"fields": [
					"activity_submission_open",
					"show_host_emails",
				]
			},
		),
		(
			"Planning",
			{
				"fields": [
					"display_planning",
					"planning_file",
					"caption_red",
					"caption_orange",
					"caption_yellow",
					"caption_green",
					"caption_blue",
					"caption_dark_blue",
					"caption_black",
				],
				"description": 'Laissez une case "Légende" vide pour la masquer',
			},
		),
		(
			"Technique",
			{
				"fields": [
					"allow_mass_mail",
					"global_message",
					"global_message_as_html",
				]
			},
		),
	]