from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import EmailUser

class InterludesActivity(models.Model):
	"""une activité des interludes (i.e. JDR, murder)..."""
	title = models.CharField("Titre", max_length=200)
	duration = models.DurationField("Durée", help_text="format hh:mm:ss")
	max_participants = models.PositiveIntegerField(
		"Nombre maximum de participants", help_text="0 pour illimité"
	)
	min_paricipants = models.PositiveIntegerField(
		"Nombre minimum de participants"
	)
	display = models.BooleanField("Afficher cette activité", default=False)
	must_subscribe = models.BooleanField("Sur inscription", default=False)
	host_name = models.CharField("Nom de l'organisateur", max_length=50)
	host_email = models.EmailField("Email de l'organisateur")
	description = models.TextField("Description", max_length=2000)
	notes = models.TextField("Notes privées", max_length=2000)

	@property
	def nb_participants(self) -> str:
		if self.max_participants == 0:
			return "Illimité"
		return "{} - {}".format(self.min_paricipants, self.max_participants)

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "activité"


class InterludesParticipant(models.Model):
	"""un participant aux interludes"""

	class ENS(models.TextChoices):
		"""enum representant les ENS"""
		ENS_ULM = "U", _("ENS Ulm")
		ENS_LYON = "L", _("ENS Lyon")
		ENS_RENNES = "R", _("ENS Rennes")
		ENS_CACHAN = "C", _("ENS Paris Saclay")

	user = models.OneToOneField(EmailUser, on_delete=models.CASCADE, related_name="Utilisateur")
	name = models.CharField("Nom complet", max_length=200)
	email = models.EmailField("email")
	school = models.CharField("ENS de rattachement", choices=ENS.choices, max_length=1)

	def __str__(self) -> str:
		return "{} ({})".format(self.name, self.school)

	class Meta:
		verbose_name = "participant"


class ActivityList(models.Model):
	"""liste d'activités souhaitée de chaque participant,
	avec un order de priorité"""
	priority = models.PositiveIntegerField("priorité")
	participant = models.ForeignKey(
		InterludesParticipant, on_delete=models.CASCADE, db_column="participant"
	)
	activity = models.ForeignKey(
		InterludesActivity, on_delete=models.CASCADE, db_column="activité"
	)

	class Meta:
		# le couple participant, priority est unique
		unique_together = (("priority", "participant"))
		ordering = ("participant", "priority")
		verbose_name = "choix d'activités"
		verbose_name_plural = "choix d'activités"
