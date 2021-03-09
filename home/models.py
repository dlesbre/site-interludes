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
	display = models.BooleanField("afficher cette activité", default=False)
	must_subscribe = models.BooleanField("sur inscription", default=False)
	host_name = models.CharField("nom de l'organisateur", max_length=50)
	host_email = models.EmailField("email de l'organisateur")
	description = models.TextField("description", max_length=2000)

	on_planning = models.BooleanField("afficher sur le planning", default=False)
	start = models.DateTimeField("début", null=True, blank=True)
	room = models.CharField("salle", max_length=100, null=True, blank=True)

	notes = models.TextField("Notes privées", max_length=2000, blank=True)

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
	school = models.CharField("ENS de rattachement", choices=ENS.choices, max_length=1)

	is_registered = models.BooleanField("est inscrit", default=False)

	meal_friday_evening = models.BooleanField("repas de vendredi soir", default=False)
	meal_saturday_morning = models.BooleanField("repas de samedi matin", default=False)
	meal_saturday_midday = models.BooleanField("repas de samedi midi", default=False)
	meal_saturday_evening = models.BooleanField("repas de samedi soir", default=False)
	meal_sunday_morning = models.BooleanField("repas de dimanche matin", default=False)
	meal_sunday_midday = models.BooleanField("repas de dimanche soir", default=False)

	sleeps = models.BooleanField("dormir sur place", default=False)

	mug = models.BooleanField("commander une tasse", default=False)

	def __str__(self) -> str:
		return "{} {} ({})".format(self.user.first_name, self.user.last_name, self.school)

	@property
	def nb_meals(self) -> int:
		return (
			self.meal_friday_evening + self.meal_saturday_evening + self.meal_saturday_midday +
			self.meal_saturday_morning + self.meal_sunday_midday + self.meal_sunday_morning
		)

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
	accepted = models.BooleanField("Obtenue", default=False)

	class Meta:
		# couples uniques
		unique_together = (("priority", "participant"), ("participant", "activity"))
		ordering = ("participant", "priority")
		verbose_name = "choix d'activités"
		verbose_name_plural = "choix d'activités"

EmailUser.profile = property(lambda user: InterludesParticipant.objects.get_or_create(user=user)[0])
