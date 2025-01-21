from django.contrib import admin

from site_settings.models import SiteSettings, SponsorModel


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
                    "hosting_school",
                    "contact_email",
                    ("date_start", "date_end"),
                    "discord_link",
                    "affiche",
                    "logo",
                    "favicon",
                ]
            },
        ),
        (
            "Tarifs",
            {
                "fields": [
                    "ticket_url",
                    ("price_entry_unpaid", "price_entry_paid"),
                    ("price_sleep_unpaid", "price_sleep_paid"),
                    ("price_friday_evening_meal_unpaid", "price_friday_evening_meal_paid"),
                    ("price_saturday_morning_meal_unpaid", "price_saturday_morning_meal_paid"),
                    ("price_saturday_midday_meal_unpaid", "price_saturday_midday_meal_paid"),
                    ("price_saturday_evening_meal_unpaid", "price_saturday_evening_meal_paid"),
                    ("price_sunday_morning_meal_unpaid", "price_sunday_morning_meal_paid"),
                    ("price_sunday_midday_meal_unpaid", "price_sunday_midday_meal_paid"),
                    ("price_sunday_evening_meal_unpaid", "price_sunday_evening_meal_paid"),
                ],
                "description": "Tarifs différentiés selon si l'élève est salarié ou non.\
                        Les tarifs des repas sont séparés en cas de besoin, mais un affichage compact\
                        est prévu si tous les repas ont le même prix (ou tous sauf le dernier).\
                        S'il ne s'affiche pas bien, vous pouvez toujours modifier les pages HTML à la main.\
                        Vous pouvez aussi désactiver certains repas dans la section repas.",
            },
        ),
        (
            "Options",
            {
                "fields": [
                    ("option1_enable", "option1_description"),
                    ("price_option1_unpaid", "price_option1_paid"),
                    ("option2_enable", "option2_description"),
                    ("price_option2_unpaid", "price_option2_paid"),
                    ("option3_enable", "option3_description"),
                    ("price_option3_unpaid", "price_option3_paid"),
                    ("option4_enable", "option4_description"),
                    ("price_option4_unpaid", "price_option4_paid"),
                    ("option5_enable", "option5_description"),
                    ("price_option5_unpaid", "price_option5_paid"),
                ],
                "description": "Les options permettent de modifier le tarif pour, "
                "par example, offrir une réduction aux adhérents BdE (tarifs négatifs), ou faire payer un peu "
                "plus pour commander des goodies.",
            },
        ),
        (
            "Activités",
            {
                "fields": [
                    "activity_submission_open",
                    "notify_on_activity_submission",
                    "show_host_emails",
                    "activities_allocated",
                ]
            },
        ),
        (
            "Inscriptions",
            {
                "fields": [
                    "registrations_open",
                    "inscriptions_open",
                    "activity_inscriptions_open",
                    ("inscriptions_start", "inscriptions_end"),
                ],
            },
        ),
        (
            "Hébergement",
            {
                "fields": [
                    "sleep_inscriptions_open",
                    "sleeper_link",
                    "sleep_host_link",
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
            "Repas",
            {
                "fields": [
                    "meal_inscriptions_open",
                    "meal_friday_evening",
                    ("meal_saturday_morning", "meal_saturday_midday", "meal_saturday_evening"),
                    ("meal_sunday_morning", "meal_sunday_midday", "meal_sunday_evening"),
                    "menu_friday_evening",
                    "menu_saturday_morning",
                    "menu_saturday_midday",
                    "menu_saturday_evening",
                    "menu_sunday_morning",
                    "menu_sunday_midday",
                    "menu_sunday_evening",
                ]
            },
        ),
        (
            "Technique",
            {
                "fields": [
                    "allow_mass_mail",
                    "orga_planning_notified",
                    "user_notified",
                    "orga_notified",
                    "global_message",
                    "global_message_as_html",
                ]
            },
        ),
    ]


@admin.register(SponsorModel)
class SponsorModelAdmin(admin.ModelAdmin):
    list_display = ["name", "display"]
    list_editable = ["display"]
    ordering = ["name"]
