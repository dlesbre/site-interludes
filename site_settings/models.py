from datetime import timedelta
from pathlib import Path
from typing import Optional, Type, TypeVar

from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.db import models


class Colors(models.TextChoices):
    """Couleur d'affichage dans le planning
    Leur code HTML est hardcodé dans la template "_planning.html"."""

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

    def __init__(self, filename="file") -> None:
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
        return cache.get(cls.__name__)

    def set_cache(self) -> None:
        """save in cache to limit db requests"""
        cache.set(self.__class__.__name__, self)


class SiteSettings(SingletonModel):
    """Réglages globaux du site"""

    contact_email = models.EmailField("Email contact", blank=True, null=True)
    date_start = models.DateField("Date de début", blank=True, null=True)
    date_end = models.DateField("Date de fin", blank=True, null=True)

    activity_submission_open = models.BooleanField(
        "Ouvrir l'ajout d'activité",
        default=False,
        help_text="Permet de proposer une activité via le formulaire dédié",
    )
    show_host_emails = models.BooleanField(
        "Afficher les mails des orgas d'activités",
        default=False,
        help_text="Ces mail sont affichés sur la page activités pour que les gens puissent les contacter",
    )

    display_planning = models.BooleanField("Afficher le planning", default=False)
    planning_file = models.FileField(
        verbose_name="Version PDF du planning",
        null=True,
        blank=True,
        storage=OverwriteStorage("Planning48hDesJeux"),
        help_text="Pour affichage sur mobile",
    )
    affiche = models.FileField(
        verbose_name="Affiche",
        null=True,
        blank=True,
        storage=OverwriteStorage("Affiche48hDesJeux"),
    )

    allow_mass_mail = models.BooleanField(
        "Permettre l'envoi de mails à tous les utilisateurs",
        default=False,
        help_text="Par sécurité, n'activez ceci qu'au moment d'envoyer les emails et désactivez le après",
    )

    notify_on_activity_submission = models.BooleanField(
        "Notification d'ajout d'activité",
        default=True,
        help_text="Envoie un email (à l'email de contact) quand une nouvelle activité est ajoutée via le formulaire.",
    )

    global_message = models.TextField(
        "Message global",
        blank=True,
        null=True,
        help_text="Message affiché en haut de chaque page (si non vide)",
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

    @property
    def contact_email_reversed(self) -> str:
        if self.contact_email is not None:
            return self.contact_email[::-1]
        return ""

    @property
    def date_2(self):
        """The date of the second day"""
        if self.date_start:
            return self.date_start + timedelta(days=1)

    @property
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
