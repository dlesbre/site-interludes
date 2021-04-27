from datetime import timedelta
from pathlib import Path

from django.db import models
from django.core.cache import cache
from django.core.files.storage import FileSystemStorage
from django.utils.timezone import now


class OverwriteStorage(FileSystemStorage):
	"""used to enforcing a fixed filename to upload file
	This allow for a constant link to a changeable file"""
	filename = "PlanningInterludes"
	def get_available_name(self, name, **kwargs):
		"""
		Returns a filename that's free on the target storage system, and
		available for new content to be written to.
		"""
		# If the filename already exists, remove it as if it was a true file system
		extension = Path(name).suffix
		new_name = self.filename + extension
		if self.exists(new_name):
			self.delete(new_name)
		return super(FileSystemStorage, self).get_available_name(new_name, **kwargs)


class SingletonModel(models.Model):
	"""Table de la BDD qui ne possède qu'un seul élément"""
	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		"""save the unique element"""
		self.pk = 1 # set private key to one
		super(SingletonModel, self).save(*args, **kwargs)
		self.set_cache()

	def delete(self, *args, **kwargs):
		"""can't delete the unique element"""
		pass

	@classmethod
	def load(cls):
		"""load and return the unique element"""
		if cache.get(cls.__name__) is None:
			obj, created = cls.objects.get_or_create(pk=1)
			if not created:
				obj.set_cache()
		return cache.get(cls.__name__)

	def set_cache(self):
		"""save in cache to limit db requests"""
		cache.set(self.__class__.__name__, self)


class SiteSettings(SingletonModel):
	"""Réglages globaux du site"""
	contact_email = models.EmailField("Email contact", blank=True, null=True)
	date_start = models.DateField("Date de début", blank=True, null=True)
	date_end = models.DateField("Date de fin", blank=True, null=True)

	registrations_open = models.BooleanField("Ouvrir la création de compte", default=False)
	inscriptions_open = models.BooleanField("Ouvrir les inscriptions", default=False)

	inscriptions_start = models.DateTimeField("Ouverture des inscriptions",
		blank=True, null=True,
		help_text="Cette date n'est qu'informative. Les inscription s'ouvrent via la checkbox uniquement"
	)
	inscriptions_end = models.DateTimeField("Fermeture des inscriptions",
		blank=True, null=True,
		help_text="Cette date n'est qu'informative. Les inscription se ferment via la checkbox uniquement"
	)

	display_planning = models.BooleanField("Afficher le planning", default=False)
	planning_file = models.FileField(
		verbose_name="Version PDF du planning", null=True, blank=True,
		storage=OverwriteStorage(),
	)

	activities_allocated = models.BooleanField(
		"Afficher les activités obtenues", default=False,
		help_text="Suppose que l'allocation des activités a été effectuée."
	)

	activity_submission_form = models.CharField(
		"Lien pour soumettre une activité", max_length=200, default="",
		blank=True, null=True
	)
	discord_link = models.CharField(
		"Lien du serveur discord", max_length=200, blank=True, null=True
	)

	allow_mass_mail = models.BooleanField(
		"Permettre l'envoi de mails collectifs (aux utilisateurs et orgas)", default=False,
		help_text="Par sécurité, n'activez ceci qu'au moment d'envoyer les emails et désactivez le après"
	)

	user_notified = models.BooleanField(
		"L'email de répartition des activités a été envoyé", default=False,
		help_text="Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Le decocher permet de renvoyer tous les mails"
	)
	orga_notified = models.BooleanField(
		"L'email de liste des participants a été envoyé", default=False,
		help_text="Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Le decocher permet de renvoyer tous les mails"
	)

	global_message = models.TextField("Message global", blank=True, null=True,
		help_text="Message affiché en haut de chaque page (si non vide)"
	)
	global_message_as_html = models.BooleanField(
		"Message global au format HTML", default=False,
		help_text="Assurez vous que le message est bien formaté, cela peut casser toutes les pages du site",
	)

	@property
	def contact_email_reversed(self) -> str:
		return self.contact_email[::-1]

	@property
	def inscriptions_not_open_yet(self) -> bool:
		if self.inscriptions_start:
			return now() <= self.inscriptions_start
		return False

	@property
	def inscriptions_have_closed(self) -> bool:
		if self.inscriptions_end:
			return now() >= self.inscriptions_end
		return False

	@property
	def date_2(self):
		"""The date of the second day"""
		if self.date_start:
			return self.date_start + timedelta(days=1)

	class Meta:
		verbose_name = "paramètres"
		verbose_name_plural = "paramètres"

	def __str__(self) -> str:
		return "Modifier les paramètres"
