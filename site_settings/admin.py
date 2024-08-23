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
                    ("price_meal_unpaid", "price_meal_paid"),
                    ("price_sleep_unpaid", "price_sleep_paid"),
                    ("price_sunday_meal_unpaid", "price_sunday_meal_paid"),
                ],
                "description": "Tarifs différentiés selon si l'élève est salarié ou non.\
                        Le repas du dimanche soir (optionel) est à part car il est à emporter.",
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
                    "meal_sunday_evening",
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
                    "user_notified",
                    "orga_notified",
                    "global_message",
                    "global_message_as_html",
                ]
            },
        ),
    ]
