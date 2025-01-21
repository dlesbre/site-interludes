from datetime import date, timedelta
from pathlib import Path
from typing import Callable, Optional, Type, TypeVar

from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


def get_year() -> int:
    """Return current school year:
    if between august and december, that is the current year + 1"""
    date = now()
    year = date.year
    if date.month >= 8:
        year += 1
    return year


class Colors(models.TextChoices):
    """Couleur d'affichage dans le planning
    Leur code HTML est hardcodé dans la template '_planning.html'."""

    RED = "a", "Rouge"
    ORANGE = "b", "Orange"
    YELLOW = "c", "Jaune"
    GREEN = "d", "Vert"
    BLUE = "e", "Bleu"
    DARK_BLUE = "f", "Bleu foncé"
    BLACK = "g", "Noir"


class OverwriteStorage(FileSystemStorage):
    """used to enforcing a fixed filename to upload file
    This allow for a constant link to a changeable file"""

    filename: str

    def __init__(self, filename: str = "file") -> None:
        """Filename without extension"""
        super().__init__()
        self.filename = filename

    def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
        """
        Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        """
        # If the filename already exists, remove it as if it was a true file system
        extension = Path(name).suffix
        new_name = self.filename + extension
        if self.exists(new_name):
            self.delete(new_name)
        return super(FileSystemStorage, self).get_available_name(new_name, max_length)


T = TypeVar("T", bound="SingletonModel")


class SingletonModel(models.Model):
    """Table de la BDD qui ne possède qu'un seul élément"""

    class Meta:
        abstract = True

    def save(self, *args, **kwargs) -> None:
        """save the unique element"""
        self.pk = 1  # set private key to one
        super(SingletonModel, self).save(*args, **kwargs)
        self.set_cache()

    def delete(self, *args, **kwargs):
        """can't delete the unique element"""
        raise ValueError("Attempting to delete unique element")

    @classmethod
    def load(cls: Type[T]) -> T:
        """load and return the unique element"""
        if cache.get(cls.__name__) is None:
            obj, created = cls.objects.get_or_create(pk=1)
            if not created:
                obj.set_cache()
        return cache.get(cls.__name__)  # type: ignore

    def set_cache(self) -> None:
        """save in cache to limit db requests"""
        cache.set(self.__class__.__name__, self)


class ENS(models.TextChoices):
    """enum representant les ENS"""

    ENS_ULM = "U", _("ENS Ulm")
    ENS_LYON = "L", _("ENS Lyon")
    ENS_RENNES = "R", _("ENS Rennes")
    ENS_CACHAN = "C", _("ENS Paris Saclay")

    def adjective(self) -> str:
        if self == "C":
            return "saclaysien"
        elif self == "L":
            return "lyonnais"
        elif self == "R":
            return "rennais"
        return "ulmite"

    def adjective_plural(self) -> str:
        if self == "C":
            return "saclaysiens"
        elif self == "L":
            return "lyonnais"
        elif self == "R":
            return "rennais"
        return "ulmites"


MEALS = [
    "friday_evening",
    "saturday_morning",
    "saturday_midday",
    "saturday_evening",
    "sunday_morning",
    "sunday_midday",
    "sunday_evening",
]

MEALS_FR = [
    "vendredi soir",
    "samedi matin",
    "samedi midi",
    "samedi soir",
    "dimanche matin",
    "dimanche midi",
    "dimanche soir",
]

OPTIONS = [
    "option1",
    "option2",
    "option3",
    "option4",
    "option5",
]


class SiteSettings(SingletonModel):
    """Réglages globaux du site

    SI VOUS AJOUTEZ DES RÉGLAGES, PENSEZ À LES RAJOUTER AUSSI DANS LES fieldsets
    DE admin.py, SINON IL N'Y APPARAITRONT PAS...
    """

    contact_email = models.EmailField("Email contact", blank=True, null=True)
    hosting_school = models.CharField(
        "École hébergeant l'événement", max_length=1, choices=ENS.choices, default=ENS.ENS_ULM
    )
    ticket_url = models.URLField(
        "Lien billeterie",
        max_length=300,
        blank=True,
        null=True,
    )

    date_start = models.DateField("Date de début", blank=True, null=True)
    date_end = models.DateField("Date de fin", blank=True, null=True)

    price_entry_unpaid = models.DecimalField(
        "prix d'inscription (non-salarié)", decimal_places=2, max_digits=5, default=0
    )
    price_entry_paid = models.DecimalField("prix d'inscription (salarié)", decimal_places=2, max_digits=5, default=0)

    price_sleep_unpaid = models.DecimalField(
        "prix d'hébergement (non-salarié)", decimal_places=2, max_digits=5, default=0
    )
    price_sleep_paid = models.DecimalField("prix d'hébergement (salarié)", decimal_places=2, max_digits=5, default=0)

    price_friday_evening_meal_unpaid = models.DecimalField(
        "prix du repas du vendredi soir (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_friday_evening_meal_paid = models.DecimalField(
        "prix du repas du vendredi soir (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    price_saturday_morning_meal_unpaid = models.DecimalField(
        "prix du repas du samedi matin (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_saturday_morning_meal_paid = models.DecimalField(
        "prix du repas du samedi matin (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    price_saturday_midday_meal_unpaid = models.DecimalField(
        "prix du repas du samedi midi (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_saturday_midday_meal_paid = models.DecimalField(
        "prix du repas du samedi midi (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    price_saturday_evening_meal_unpaid = models.DecimalField(
        "prix du repas du samedi soir (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_saturday_evening_meal_paid = models.DecimalField(
        "prix du repas du samedi soir (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    price_sunday_morning_meal_unpaid = models.DecimalField(
        "prix du repas du dimanche matin (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_sunday_morning_meal_paid = models.DecimalField(
        "prix du repas du dimanche matin (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    price_sunday_midday_meal_unpaid = models.DecimalField(
        "prix du repas du dimanche midi (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_sunday_midday_meal_paid = models.DecimalField(
        "prix du repas du dimanche midi (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    price_sunday_evening_meal_unpaid = models.DecimalField(
        "prix du repas du dimanche soir (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_sunday_evening_meal_paid = models.DecimalField(
        "prix du repas du dimanche soir (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    option1_enable = models.BooleanField(
        "Option 1",
        default=False,
    )
    option1_description = models.CharField(
        "Description Option 1",
        blank=True,
        null=True,
        help_text="ex: 'Adhérent du COF', 'Commande un Mug'...",
        max_length=200,
    )
    price_option1_paid = models.DecimalField(
        "prix option 1 (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_option1_unpaid = models.DecimalField(
        "prix option 1 (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    option2_enable = models.BooleanField(
        "Option 2",
        default=False,
    )
    option2_description = models.CharField(
        "Description Option 2",
        blank=True,
        null=True,
        max_length=200,
    )
    price_option2_paid = models.DecimalField(
        "prix option 2 (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_option2_unpaid = models.DecimalField(
        "prix option 2 (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    option3_enable = models.BooleanField(
        "Option 3",
        default=False,
    )
    option3_description = models.CharField(
        "Description Option 3",
        blank=True,
        null=True,
        max_length=200,
    )
    price_option3_paid = models.DecimalField(
        "prix option 3 (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_option3_unpaid = models.DecimalField(
        "prix option 3 (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    option4_enable = models.BooleanField(
        "Option 4",
        default=False,
    )
    option4_description = models.CharField(
        "Description Option 4",
        blank=True,
        null=True,
        max_length=200,
    )
    price_option4_paid = models.DecimalField(
        "prix option 4 (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_option4_unpaid = models.DecimalField(
        "prix option 4 (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    option5_enable = models.BooleanField(
        "Option 5",
        default=False,
    )
    option5_description = models.CharField(
        "Description Option 5",
        blank=True,
        null=True,
        max_length=200,
    )
    price_option5_paid = models.DecimalField(
        "prix option 5 (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_option5_unpaid = models.DecimalField(
        "prix option 5 (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    @staticmethod
    def pretty_price(name: str) -> Callable[["SiteSettings"], str]:
        def pp(self):
            paid = getattr(self, "price_" + name + "_paid")
            unpaid = getattr(self, "price_" + name + "_unpaid")
            if paid == unpaid:
                return "{}€".format(paid)
            return "{}€ / {}€".format(paid, unpaid)

        return pp

    price_entry = pretty_price("entry")
    price_sleep = pretty_price("sleep")
    price_friday_evening_meal = pretty_price("friday_evening_meal")
    price_saturday_morning_meal = pretty_price("saturday_morning_meal")
    price_saturday_midday_meal = pretty_price("saturday_midday_meal")
    price_saturday_evening_meal = pretty_price("saturday_evening_meal")
    price_sunday_morning_meal = pretty_price("sunday_morning_meal")
    price_sunday_midday_meal = pretty_price("sunday_midday_meal")
    price_sunday_evening_meal = pretty_price("sunday_evening_meal")
    price_option1 = pretty_price("option1")
    price_option2 = pretty_price("option2")
    price_option3 = pretty_price("option3")
    price_option4 = pretty_price("option4")
    price_option5 = pretty_price("option5")

    meal_friday_evening = models.BooleanField("Repas vendredi soir", default=True)
    meal_saturday_morning = models.BooleanField("Repas samedi matin", default=True)
    meal_saturday_midday = models.BooleanField("Repas samedi midi", default=True)
    meal_saturday_evening = models.BooleanField("Repas samedi soir", default=True)
    meal_sunday_morning = models.BooleanField("Repas dimanche matin", default=True)
    meal_sunday_midday = models.BooleanField("Repas dimanche midi", default=True)
    meal_sunday_evening = models.BooleanField("Repas dimanche soir", default=True)

    def any_meal(self) -> bool:
        return (
            self.meal_friday_evening
            or self.meal_saturday_morning
            or self.meal_saturday_midday
            or self.meal_saturday_evening
            or self.meal_sunday_morning
            or self.meal_sunday_midday
            or self.meal_sunday_evening
        )

    menu_friday_evening = models.CharField("Menu du repas de vendredi soir", blank=True, max_length=400, default="")
    menu_saturday_morning = models.CharField("Menu du repas de samedi matin", blank=True, max_length=400, default="")
    menu_saturday_midday = models.CharField("Menu du repas de samedi midi", blank=True, max_length=400, default="")
    menu_saturday_evening = models.CharField("Menu du repas de samedi soir", blank=True, max_length=400, default="")
    menu_sunday_morning = models.CharField("Menu du repas de dimanche matin", blank=True, max_length=400, default="")
    menu_sunday_midday = models.CharField("Menu du repas de dimanche midi", blank=True, max_length=400, default="")
    menu_sunday_evening = models.CharField("Menu du repas de dimanche soir", blank=True, max_length=400, default="")

    def menus(self) -> bool:
        """Check if any menu is defined before displaying them"""
        return (
            self.menu_friday_evening != ""
            or self.menu_saturday_morning != ""
            or self.menu_saturday_midday != ""
            or self.menu_saturday_evening != ""
            or self.menu_sunday_morning != ""
            or self.menu_sunday_midday != ""
            or self.menu_sunday_evening != ""
        )

    def pretty_meal_prices(self) -> str:
        if not self.any_meal():
            return ""
        all_meals = []
        for i, meal in enumerate(MEALS):
            if getattr(self, "meal_" + meal):
                all_meals.append((MEALS_FR[i], getattr(self, "price_" + meal + "_meal")()))
        if all(x[1] == all_meals[0][1] for x in all_meals):
            # All meals have the same price
            return "<li><strong>Repas&nbsp;:</strong> {} par repas</li>".format(all_meals[0][1])
        elif len(all_meals) >= 3 and all(x[1] == all_meals[0][1] for x in all_meals[:-1]):
            # All meals but the last one have the same price
            return "<li><strong>Repas (du {} au {})&nbsp;:</strong> {} par repas</li>\n\
                <li><strong>Repas du {}&nbsp;:</strong> {}</li>".format(
                all_meals[0][0], all_meals[-2][0], all_meals[0][1], all_meals[-1][0], all_meals[-1][1]
            )
        return "\n".join(
            "<li><strong>Repas du {}&nbsp;:</strong> {}</li>".format(meal, price) for meal, price in all_meals
        )

    registrations_open = models.BooleanField("Ouvrir la création de compte", default=True)
    inscriptions_open = models.BooleanField(
        "Ouvrir les inscriptions",
        default=False,
        help_text="Permet d'ouvrir le formulaire d'inscription (repas et dodo; l'inscription aux activité est ouvrable en plus)",
    )
    activity_inscriptions_open = models.BooleanField(
        "Ouvrir l'inscription aux activitées",
        default=False,
        help_text="Permet d'ouvrir la partie du formulaire d'inscription pour les activités (nécessite l'ouverture des inscriptions)",
    )
    meal_inscriptions_open = models.BooleanField(
        "Ouvrir l'inscription aux repas",
        default=True,
        help_text="Permet de s'inscrire aux repas sur le formulaire d'inscription.",
    )
    sleep_inscriptions_open = models.BooleanField(
        "Ouvrir l'inscription à l'hébergement",
        default=True,
        help_text="Permet de s'inscrire à l'hébergement sur le formulaire d'inscription.",
    )
    activity_submission_open = models.BooleanField(
        "Ouvrir l'ajout d'activité",
        default=False,
        help_text="Permet de proposer une activité via le formulaire dédié. Nécessite d'ouvrir la création de comptes.",
    )
    notify_on_activity_submission = models.BooleanField(
        "Notification d'ajout d'activité",
        default=True,
        help_text="Envoie un email (à l'email de contact) lorsqu'une nouvelle activité est ajoutée via le formulaire.",
    )
    show_host_emails = models.BooleanField(
        "Afficher les mails des orgas d'activités",
        default=False,
        help_text="Ces mail sont affichés sur la page activités pour qu'ils puissent être contactés",
    )

    inscriptions_start = models.DateTimeField(
        "Ouverture des inscriptions",
        blank=True,
        null=True,
        help_text="Cette date n'est qu'informative. Les inscription s'ouvrent via la checkbox uniquement",
    )
    inscriptions_end = models.DateTimeField(
        "Fermeture des inscriptions",
        blank=True,
        null=True,
        help_text="Cette date n'est qu'informative. Les inscription se ferment via la checkbox uniquement",
    )

    display_planning = models.BooleanField("Afficher le planning", default=False)
    planning_file = models.FileField(
        verbose_name="Version image ou PDF du planning",
        null=True,
        blank=True,
        storage=OverwriteStorage("PlanningInterludes"),
        help_text="Le planning autogénéré n'est pas très lisible sur mobile. Je conseille d'en faire une capture sur grand écran et l'ajouter ici.",
    )
    affiche = models.FileField(
        verbose_name="Affiche",
        null=True,
        blank=True,
        storage=OverwriteStorage("AfficheInterludes"),
    )
    logo = models.FileField(
        verbose_name="Logo",
        help_text="Apparait dans le header",
        null=True,
        blank=True,
        storage=OverwriteStorage("LogoInterludes"),
    )
    favicon = models.FileField(
        verbose_name="Favicon",
        help_text="Icône du site, image au format .ico",
        null=True,
        blank=True,
        storage=OverwriteStorage("favicon"),
    )

    activities_allocated = models.BooleanField(
        "Afficher les activités obtenues",
        default=False,
        help_text="Une fois que l'allocation des activités a été effectuée.",
    )

    discord_link = models.URLField("Lien du serveur discord", max_length=200, blank=True, null=True)
    sleeper_link = models.URLField("Lien du formulaire de demande d'hébergement", max_length=200, blank=True, null=True)
    sleep_host_link = models.URLField(
        "Lien du formulaire de proposition d'hébergement", max_length=200, blank=True, null=True
    )

    allow_mass_mail = models.BooleanField(
        "Permettre l'envoi de mails collectifs (aux utilisateurs et orgas)",
        default=False,
        help_text="Par sécurité, n'activez ceci qu'au moment d'envoyer les emails et désactivez le après",
    )

    user_notified = models.DateTimeField(
        "Dernier envoie de l'email de répartition des activités",
        blank=True,
        null=True,
        help_text="Email donnant à chaque participant la liste des activités qu'il a obtenu. Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Mettez le à vide pour ré-envoyer un email",
    )
    orga_notified = models.DateTimeField(
        "Dernier envoie de l'email de liste des participants",
        blank=True,
        null=True,
        help_text="Email donnant à chaque orga d'activité (qui le demande) la liste des participants inscrit à son activite. Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Mettez le à vide pour ré-envoyer un email",
    )
    orga_planning_notified = models.DateTimeField(
        "Dernier envoie de l'email communiquant leurs créneaux aux orgas",
        blank=True,
        null=True,
        help_text="Email donnant aux organisateurs d'activité leurs créneaux. Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Mettez le à vide pour ré-envoyer un email",
    )

    global_message = models.TextField(
        "Message global",
        blank=True,
        null=True,
        help_text='Message affiché en haut de chaque page (si non vide). Vous pouvez également modifier le contenu de certaines pages depuis "Pages HTML"',
    )
    global_message_as_html = models.BooleanField(
        "Message global au format HTML",
        default=False,
        help_text="Assurez vous que le message est bien formaté, cela peut casser toutes les pages du site",
    )

    # Légende du planning modifiable
    caption_red = models.CharField(
        "Légende planning (rouge)",
        default="Jeux de rôle grandeur nature",
        blank=True,
        null=True,
        max_length=200,
    )
    caption_orange = models.CharField(
        "Légende planning (orange)",
        default="Jeux de rôle sur table",
        blank=True,
        null=True,
        max_length=200,
    )
    caption_yellow = models.CharField(
        "Légende planning (jaune)",
        default="Activités libres",
        blank=True,
        null=True,
        max_length=200,
    )
    caption_green = models.CharField(
        "Légende planning (vert)",
        default="Tournois",
        blank=True,
        null=True,
        max_length=200,
    )
    caption_blue = models.CharField(
        "Légende planning (bleu)",
        default="Événements de début et fin",
        blank=True,
        null=True,
        max_length=200,
    )
    caption_dark_blue = models.CharField(
        "Légende planning (bleu foncé)",
        default="Jeux vidéos",
        blank=True,
        null=True,
        max_length=200,
    )
    caption_black = models.CharField(
        "Légende planning (noir)",
        default="Autre",
        blank=True,
        null=True,
        max_length=200,
    )

    def contact_email_reversed(self) -> str:
        if self.contact_email:
            return self.contact_email[::-1]
        return ""

    def inscriptions_not_open_yet(self) -> bool:
        if self.inscriptions_start:
            return now() <= self.inscriptions_start
        return False

    def inscriptions_have_closed(self) -> bool:
        if self.inscriptions_end:
            return now() >= self.inscriptions_end
        return False

    def date_2(self) -> date | None:
        """The date of the second day"""
        if self.date_start:
            return self.date_start + timedelta(days=1)
        return None

    def has_caption(self) -> bool:
        """Vérifie si l'une des légende est non-nulle"""
        return bool(
            self.caption_red
            or self.caption_orange
            or self.caption_yellow
            or self.caption_green
            or self.caption_blue
            or self.caption_dark_blue
            or self.caption_black
        )

    class Meta:
        verbose_name = "paramètres"
        verbose_name_plural = "paramètres"

    def __str__(self) -> str:
        return "Modifier les paramètres"

    def hosting_school_adjective(self) -> str:
        return ENS(self.hosting_school).adjective()

    def hosting_school_adjective_plural(self) -> str:
        return ENS(self.hosting_school).adjective_plural()


class SponsorModel(models.Model):
    """Model for footer sponser logos"""

    name = models.CharField(
        "nom",
        max_length=100,
        help_text="L'affichage des sponsors se fait par order alphabétique",
    )
    display = models.BooleanField(
        "Affiché",
        default=False,
    )
    image = models.FileField("logo")
    url = models.URLField("lien")
    alt_text = models.CharField(
        "alt-text",
        max_length=100,
        help_text="S'affiche si l'image ne peut pas être chargée",
    )

    class Meta:
        # couples uniques
        ordering = ("name",)
        verbose_name = "sponsor"
        verbose_name_plural = "sponsors"
