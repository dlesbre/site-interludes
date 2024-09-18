from typing import TYPE_CHECKING, Optional

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models

from shared.models import normalize_email

if TYPE_CHECKING:
    # Only import when type-checking to avoid circular dependency
    from home.models import ParticipantModel


class EmailUserManager(UserManager["AbstractUser"]):
    """User model manager that replaces username with email"""

    def create_user(self, email: str, password: str, **extra_fields):  # type: ignore
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("Creating user with no email")
        email = normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class EmailUser(AbstractUser):
    """Utilisateur identifié par son email et non
    un nom d'utilisateur"""

    profile: "ParticipantModel"
    clipper_account: "Optional[ClipperAccount]"

    username = None  # type: ignore
    email = models.EmailField("adresse email", unique=True)
    first_name = models.CharField("prénom", max_length=100)
    last_name = models.CharField("nom", max_length=100)
    email_confirmed = models.BooleanField("email vérifié", default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["last_name", "first_name"]

    objects: UserManager["EmailUser"] = EmailUserManager()  # type: ignore

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "utilisateur"


class ClipperAccount(models.Model):
    """Information about Clipper accounts (ENS ULM).

    A user is given an instance of this model iff they have a Clipper account.

    Instances of this model should only be created by the `ClipperBackend` authentication
    backend.
    """

    user = models.OneToOneField(
        EmailUser,
        verbose_name="utilisateur",
        on_delete=models.CASCADE,
        related_name="clipper_account",
    )
    clipper_login = models.CharField(
        verbose_name="login clipper",
        max_length=20,
        blank=False,
        unique=True,
    )
    unique_id = models.CharField(
        verbose_name="identifiant unique",
        max_length=1023,
        blank=False,
        help_text="Les logins clipper sont rarements unique, mais le combo login+homedir l'est souvent",
    )

    class Meta:
        verbose_name = "Compte Clipper"
        verbose_name_plural = "Comptes Clipper"

    def __str__(self):
        return "{} ({})".format(
            self.clipper_login,
            self.user.email,
        )
