from django.contrib import admin

from home import models
from shared.admin import ExportCsvMixin

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site 48h des Jeux"
# Tag html <title>
admin.site.site_title = "Admin 48h des jeux"


@admin.register(models.ActivityModel)
class ActivityModelAdmin(ExportCsvMixin, admin.ModelAdmin):
    """option d'affichage des activités dans la vue django admin"""

    filename = "export_activites.csv"
    list_display = (
        "title",
        "host_name",
        "display",
        "must_subscribe",
    )
    list_filter = (
        "display",
        "must_subscribe",
        "year",
    )
    ordering = (
        "title",
        "host_name",
    )
    list_editable = ("display",)
    fieldsets = [
        (
            "",
            {
                "fields": [
                    "title",
                    "display",
                    "year",
                ]
            },
        ),
        (
            "Organisateurs",
            {
                "fields": [
                    "host",
                    ("host_name", "host_email"),
                    "host_info",
                ]
            },
        ),
        (
            "Informations publiques",
            {
                "fields": [
                    "show_email",
                    "act_type",
                    "game_type",
                    "duration",
                    ("min_participants", "max_participants"),
                    "must_subscribe",
                    "description",
                    "desc_as_html",
                ]
            },
        ),
        (
            "Créneau",
            {
                "fields": [
                    "desired_slot_nb",
                    (
                        "available_friday_evening",
                        "available_friday_night",
                        "available_saturday_morning",
                        "available_saturday_afternoon",
                        "available_saturday_evening",
                        "available_saturday_night",
                        "available_sunday_morning",
                        "available_sunday_afternoon",
                    ),
                    "constraints",
                ]
            },
        ),
        (
            "Autre informations",
            {
                "fields": [
                    "needs",
                    "comments",
                ]
            },
        ),
    ]
    list_per_page = 100
    csv_export_fields = [
        # The key is "host_id" but listed as "host" in auto-found field names
        # which leads to an error...
        "id",
        "year",
        "display",
        "title",
        "act_type",
        "game_type",
        "description",
        "desc_as_html",
        "host_id",
        "host_name",
        "host_email",
        "show_email",
        "host_info",
        "must_subscribe",
        "max_participants",
        "min_participants",
        "duration",
        "desired_slot_nb",
        "available_friday_evening",
        "available_friday_night",
        "available_saturday_morning",
        "available_saturday_afternoon",
        "available_saturday_evening",
        "available_saturday_night",
        "available_sunday_morning",
        "available_sunday_afternoon",
        "constraints",
        "needs",
        "comments",
    ]


@admin.register(models.SlotModel)
class SlotModelAdmin(ExportCsvMixin, admin.ModelAdmin):
    """option d'affichage des créneaux dans la vue d'admin"""

    filename = "export_slots.csv"
    csv_export_fields = [
        "activity_id",
        "title",
        "start",
        "duration",
        "room",
        "on_planning",
        "on_activity",
        "color",
    ]
    list_display = (
        "__str__",
        "start",
        "room",
        "on_planning",
        "on_activity",
    )
    list_filter = (
        "on_planning",
        "activity__display",
    )
    list_editable = (
        "on_planning",
        "on_activity",
    )
    ordering = (
        "activity",
        "title",
        "start",
    )
