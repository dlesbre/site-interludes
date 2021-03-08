from django.db import models
from django.core.cache import cache

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

	display_planning = models.BooleanField("Afficher le planning", default=False)

	@property
	def contact_email_reversed(self):
		return self.contact_email[::-1]

	class Meta:
		verbose_name = "paramètres"

	def __str__(self) -> str:
		return "Modifier les paramètres"
