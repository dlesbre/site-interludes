from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Type, TypeVar

from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.utils.timezone import now


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


class SiteSettings(SingletonModel):
    """Réglages globaux du site

    SI VOUS AJOUTEZ DES RÉGLAGES, PENSEZ À LES RAJOUTER AUSSI DANS LES fieldsets
    DE admin.py, SINON IL N'Y APPARAITRONT PAS...
    """

    contact_email = models.EmailField("Email contact", blank=True, null=True)
    hosting_school = models.CharField(
        "École hébergeant l'événement",
        max_length=50,
        blank=True,
        null=True,
    )
    ticket_url = models.CharField(
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
    price_entry_paid = models.DecimalField(
        "prix d'inscription (salarié)", decimal_places=2, max_digits=5, default=0
    )

    def price_entry(self) -> str:
        if self.price_entry_paid == self.price_entry_unpaid:
            return "{}€".format(self.price_entry_paid)
        return "{}€ / {}€".format(self.price_entry_paid, self.price_entry_unpaid)

    price_meal_unpaid = models.DecimalField(
        "prix d'un repas (non-salarié)", decimal_places=2, max_digits=5, default=0
    )
    price_meal_paid = models.DecimalField(
        "prix d'un repas (salarié)", decimal_places=2, max_digits=5, default=0
    )

    def price_meal(self) -> str:
        if self.price_meal_paid == self.price_meal_unpaid:
            return "{}€".format(self.price_meal_paid)
        return "{}€ / {}€".format(self.price_meal_paid, self.price_meal_unpaid)

    price_sleep_unpaid = models.DecimalField(
        "prix d'hébergement (non-salarié)", decimal_places=2, max_digits=5, default=0
    )
    price_sleep_paid = models.DecimalField(
        "prix d'hébergement (salarié)", decimal_places=2, max_digits=5, default=0
    )

    def price_sleep(self) -> str:
        if self.price_sleep_paid == self.price_sleep_unpaid:
            return "{}€".format(self.price_sleep_paid)
        return "{}€ / {}€".format(self.price_sleep_paid, self.price_sleep_unpaid)

    price_sunday_meal_unpaid = models.DecimalField(
        "prix du repas du dimanche soir (non-salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )
    price_sunday_meal_paid = models.DecimalField(
        "prix du repas du dimanche soir (salarié)",
        decimal_places=2,
        max_digits=5,
        default=0,
    )

    meal_sunday_evening = models.BooleanField(
        "Repas dimanche soir (à emporter)", default=True
    )

    menu_friday_evening = models.CharField(
        "Menu du repas de vendredi soir", blank=True, max_length=400, default=""
    )
    menu_saturday_morning = models.CharField(
        "Menu du repas de samedi matin", blank=True, max_length=400, default=""
    )
    menu_saturday_midday = models.CharField(
        "Menu du repas de samedi midi", blank=True, max_length=400, default=""
    )
    menu_saturday_evening = models.CharField(
        "Menu du repas de samedi soir", blank=True, max_length=400, default=""
    )
    menu_sunday_morning = models.CharField(
        "Menu du repas de dimanche matin", blank=True, max_length=400, default=""
    )
    menu_sunday_midday = models.CharField(
        "Menu du repas de dimanche midi", blank=True, max_length=400, default=""
    )
    menu_sunday_evening = models.CharField(
        "Menu du repas de dimanche soir", blank=True, max_length=400, default=""
    )

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

    def price_sunday_meal(self) -> str:
        if self.price_sunday_meal_paid == self.price_sunday_meal_unpaid:
            return "{}€".format(self.price_sunday_meal_paid)
        return "{}€ / {}€".format(
            self.price_sunday_meal_paid, self.price_sunday_meal_unpaid
        )

    registrations_open = models.BooleanField(
        "Ouvrir la création de compte", default=True
    )
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
    activity_submission_open = models.BooleanField(
        "Ouvrir l'ajout d'activité",
        default=False,
        help_text="Permet de proposer une activité via le formulaire dédié. Nécessite d'ouvrir la création de comptes.",
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
        verbose_name="Version PDF du planning",
        null=True,
        blank=True,
        storage=OverwriteStorage("PlanningInterludes"),
    )
    affiche = models.FileField(
        verbose_name="Affiche",
        null=True,
        blank=True,
        storage=OverwriteStorage("AfficheInterludes"),
    )

    activities_allocated = models.BooleanField(
        "Afficher les activités obtenues",
        default=False,
        help_text="Une fois que l'allocation des activités a été effectuée.",
    )

    discord_link = models.CharField(
        "Lien du serveur discord", max_length=200, blank=True, null=True
    )

    allow_mass_mail = models.BooleanField(
        "Permettre l'envoi de mails collectifs (aux utilisateurs et orgas)",
        default=False,
        help_text="Par sécurité, n'activez ceci qu'au moment d'envoyer les emails et désactivez le après",
    )

    user_notified = models.BooleanField(
        "L'email de répartition des activités a été envoyé",
        default=False,
        help_text="Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Le decocher permet de renvoyer tous les mails",
    )
    orga_notified = models.BooleanField(
        "L'email de liste des participants a été envoyé",
        default=False,
        help_text="Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Le decocher permet de renvoyer tous les mails",
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
