from django.contrib import admin

from home import models
from shared.admin import ExportCsvMixin

# Titre de la vue (tag <h1>)
admin.site.site_header = "Administration site interludes"
# Tag html <title>
admin.site.site_title = "Admin Interludes"


@admin.register(models.ActivityModel)
class ActivityModelAdmin(ExportCsvMixin):
    """option d'affichage des activités dans la vue django admin"""

    filename = "export_activites.csv"
    list_display = (
        "title",
        "host_name",
        "display",
        "must_subscribe",
        "year",
    )
    list_filter = (
        "year",
        "display",
        "must_subscribe",
        "status",
    )
    ordering = (
        "-year",
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
            "Organisateurs/MJ",
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
                    ("min_participants", "max_participants"),
                    ("must_subscribe", "communicate_participants"),
                    "duration",
                    "description",
                    "desc_as_html",
                ],
                "description": "Ces informations apparaissent sur la page activités",
            },
        ),
        (
            "Créneaux",
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
                    "status",
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
        "display",
        "title",
        "year",
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
        "communicate_participants",
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
        "status",
        "needs",
        "comments",
    ]


@admin.register(models.SlotModel)
class SlotModelAdmin(ExportCsvMixin):
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
        "subscribing_open",
        "on_planning",
        "on_activity",
    )
    list_filter = (
        "activity__year",
        "activity__display",
        "subscribing_open",
        "on_planning",
        "on_activity",
    )
    list_editable = (
        "subscribing_open",
        "on_planning",
        "on_activity",
    )
    ordering = (
        "activity",
        "title",
        "start",
    )


@admin.register(models.ParticipantModel)
class ParticipantModelAdmin(ExportCsvMixin):
    """option d'affichage des participant dans la vue django admin"""

    filename = "export_participants.csv"
    fieldsets = [
        (
            "",
            {
                "fields": [
                    "user",
                    "school",
                ]
            },
        ),
        (
            "Inscription",
            {
                "fields": [
                    "is_registered",
                    (
                        "meal_friday_evening",
                        "meal_saturday_morning",
                        "meal_saturday_midday",
                        "meal_saturday_evening",
                        "meal_sunday_morning",
                        "meal_sunday_midday",
                        "meal_sunday_evening",
                    ),
                    (
                        "option1",
                        "option2",
                        "option3",
                        "option4",
                        "option5",
                    ),
                    "sleeps",
                    "paid",
                    "amount_paid",
                    "comment",
                ]
            },
        ),
        (
            "Expérience murder",
            {
                "fields": [
                    "nb_murder",
                    "extra_contact",
                    "murder_comment",
                ]
            },
        ),
    ]
    list_display = ("user", "school", "is_registered", "comment", "cost")
    list_filter = (
        "school",
        "is_registered",
        "sleeps",
        "meal_friday_evening",
        "meal_saturday_morning",
        "meal_saturday_midday",
        "meal_saturday_evening",
        "meal_sunday_morning",
        "meal_sunday_midday",
        "meal_sunday_evening",
        "nb_murder",
        "paid",
    )
    ordering = ("user",)
    list_per_page = 200


@admin.register(models.ActivityChoicesModel)
class ActivityListAdmin(ExportCsvMixin):
    """option d'affichage des choix d'activités dans la vue django admin"""

    filename = "export_choix_activite.csv"
    list_display = ("slot", "participant", "priority", "accepted")
    list_filter = (
        "slot__activity",
        "participant__is_registered",
        "slot__activity__display",
        "accepted",
        "slot__subscribing_open",
    )
    list_editable = ("accepted",)
    ordering = (
        "slot",
        "priority",
        "participant",
    )
    list_per_page = 400
