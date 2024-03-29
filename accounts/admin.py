from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import EmailUser
from shared.admin import ExportCsvMixin

# no need for groups - we only have regular users and superusers
admin.site.unregister(Group)


@admin.register(EmailUser)
class EmailUserAdmin(ExportCsvMixin):
    """option d'affichage des activités dans la vue django admin"""

    filename = "export_utilisateurs.csv"
    list_display = (
        "email",
        "last_name",
        "first_name",
        "is_superuser",
        "is_active",
        "email_confirmed",
    )
    list_filter = (
        "is_superuser",
        "is_active",
        "email_confirmed",
    )
    fields = (
        "email",
        "last_name",
        "first_name",
        "is_superuser",
        "is_staff",
        "is_active",
        "email_confirmed",
        (
            "date_joined",
            "last_login",
        ),
    )
    ordering = ("last_name", "first_name")
    readonly_fields = (
        "date_joined",
        "last_login",
    )
    list_per_page = 200

    csv_export_exclude = ["password"]
