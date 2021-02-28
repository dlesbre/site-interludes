from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class InterludesActivity(models.Model):
	"""une activité des interludes (i.e. JDR, murder)..."""
	title = models.CharField("Titre", max_length=200)
	duration = models.DurationField("Durée", help_text="format hh:mm:ss")
	display = models.BooleanField("Afficher cette activité", default=False)
	host_name = models.CharField("Nom de l'organisateur", max_length=50)
	host_email = models.EmailField("Email de l'organisateur")
	description = models.TextField("Description", max_length=2000)

class InterludesParticipant(models.Model):
	"""un participant aux interludes"""

	class ENS(models.TextChoices):
		"""enum representant les ENS"""
		ENS_ULM = "U", _("ENS Ulm")
		ENS_LYON = "L", _("ENS Lyon")
		ENS_RENNES = "R", _("ENS Rennes")
		ENS_CACHAN = "C", _("ENS Paris Saclay")

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="Utilisateur")
	name = models.CharField("Nom complet", max_length=200)
	email = models.EmailField("email")
	school = models.CharField("ENS de rattachement", choices=ENS.choices, max_length=1)

class ActivityList(models.Model):
	"""liste d'activités souhaitée de chaque participant,
	avec un order de priorité"""
	priority = models.PositiveIntegerField()
	participant = models.ForeignKey(InterludesParticipant, on_delete=models.CASCADE)
	activite = models.ForeignKey(InterludesActivity, on_delete=models.CASCADE)

	class Meta:
		# le couple participant, priority est unique
		unique_together = (("priority", "participant"))
