from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import EmailUser

# no need for groups - we only have regular users and superusers
admin.site.unregister(Group)

@admin.register(EmailUser)
class EmailUserAdmin(admin.ModelAdmin):
	"""option d'affichage des activités dans la vue django admin"""
	list_display = ("email", "last_name", "first_name", "is_superuser")
	list_filter = ("is_superuser",)
	list_editable = ("is_superuser",)
	ordering = ("last_name", "first_name")
	readonly_fields = ("date_joined", "last_login",)
	exclude = ("groups","password",)
	list_per_page = 200
