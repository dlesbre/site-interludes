import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts.models import EmailUser
from site_settings.models import Colors, SiteSettings

def validate_nonzero(value):
	"""Make a positive integer field non-zero"""
	if value == 0:
		raise ValidationError(
			_('Cette valeur doit-être non-nulle'),
		)

class ActivityModel(models.Model):
	"""une activité des interludes (i.e. JDR, murder)..."""

	class Status(models.TextChoices):
		"""en presentiel ou non"""
		PRESENT = "P", _("En présentiel uniquement")
		DISTANT = "D", _("En distanciel uniquement")
		BOTH = "2", _("Les deux")

	class ActivityTypes(models.TextChoices):
		"""quantité d'activité"""
		GAME = "1 partie", _("Une partie")
		GAMES = "2+ parties", _("Quelques parties")
		TOURNAMENT = "Tournoi", _("Tournoi")
		FREEPLAY = "freeplay", _("Freeplay")
		OTHER = "other", _("Autre")

	class GameTypes(models.TextChoices):
		"""types de jeu"""
		CARD_GAME = "jeu cartes", _("Jeu de cartes")
		BOARD_GAME = "jeu plateau", _("Jeu de société")
		TABLETOP_RPG = "table RPG", _("Jeu de rôle sur table")
		LARGE_RPG = "large RPG", _("Jeu de rôle grandeur nature")
		VIDEOGAME = "videogame", _("Jeu vidéo")
		PARTYGAME = "partygame", _("Party game")
		PUZZLE = "puzzle", _("Puzzle ou analogue")
		SECRET_ROLES = "secret roles", _("Jeu à rôles secrets")
		COOP = "coop", _("Jeu coopératif")
		OTHER = "other", _("Autre")

	class Availability(models.TextChoices):
		"""Diponibilité à un moment donné"""
		IDEAL = "0", _("Idéal")
		POSSIBLE = "1", _("Acceptable")
		UNAVAILABLE = "2", _("Indisponible")

	display = models.BooleanField("afficher dans la liste", default=False,
		help_text="Si vrai, s'affiche sur la page activités"
	)

	title = models.CharField("Titre", max_length=200)

	act_type = models.CharField("Type d'activité", choices=ActivityTypes.choices, max_length=12)
	game_type = models.CharField("Type de jeu", choices=GameTypes.choices, max_length=12)
	description = models.TextField(
		"description", max_length=10000,
		help_text='Texte ou html selon la valeur de "Description HTML".\n'
	)
	desc_as_html = models.BooleanField("Description au format HTML", default=False,
		help_text="Assurer vous que le texte est bien formaté, cette option peut casser la page activités."
	)

	host = models.ForeignKey(
		EmailUser, on_delete=models.SET_NULL, verbose_name="Organisateur",
		blank=True, null=True
	)
	host_name = models.CharField(
		"nom de l'organisateur", max_length=50, null=True, blank=True,
		help_text="Peut-être laissé vide pour des simples activités sans orga"
	)
	host_email = models.EmailField(
		"email de l'organisateur",
		help_text="Utilisé pour communiquer la liste des participants si demandé"
	)
	host_info = models.TextField(
		"Autre orgas/contacts", max_length=1000, blank=True, null=True
	)

	must_subscribe = models.BooleanField("sur inscription", default=False,
		help_text="Informatif, il faut utiliser les créneaux pour ajouter dans la liste d'inscription"
	)
	communicate_participants = models.BooleanField("communiquer la liste des participants à l'orga avant l'événement")
	max_participants = models.PositiveIntegerField(
		"Nombre maximum de participants", help_text="0 pour illimité", default=0
	)
	min_participants = models.PositiveIntegerField(
		"Nombre minimum de participants", default=0
	)

	## Information fournies par le respo
	duration = models.DurationField("Durée", help_text="format hh:mm:ss")
	desired_slot_nb = models.PositiveIntegerField(
		"Nombre de créneaux souhaités", default=1,
		validators=[validate_nonzero]
	)

	available_friday_evening = models.CharField(
		"Crénau vendredi soir", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_friday_night = models.CharField(
		"Crénau vendredi nuit", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_saturday_morning = models.CharField(
		"Crénau samedi matin", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_saturday_afternoon = models.CharField(
		"Crénau samedi après-midi", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_saturday_evening = models.CharField(
		"Crénau samedi soir", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_saturday_night = models.CharField(
		"Crénau samedi nuit", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_sunday_morning = models.CharField(
		"Crénau dimanche matin", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)
	available_sunday_afternoon = models.CharField(
		"Crénau dimanche après-midi", choices=Availability.choices, max_length=1,
		default=Availability.POSSIBLE,
	)

	constraints = models.TextField(
		"Contraintes particulières", max_length=2000, blank=True, null=True
	)

	status = models.CharField("Présentiel/distanciel", choices=Status.choices, max_length=1)
	needs = models.TextField(
		"Besoin particuliers", max_length=2000, blank=True, null=True
	)

	comments = models.TextField(
		"Commentaires", max_length=2000, blank=True, null=True
	)

	@property
	def nb_participants(self) -> str:
		if self.max_participants == 0:
			ret = "Illimités"
		elif self.max_participants == self.min_participants:
			ret = "{}".format(self.min_participants)
		else:
			ret = "{} - {}".format(self.min_participants, self.max_participants)
		if self.must_subscribe:
			ret += " (sur inscription)"
		return ret

	@property
	def pretty_duration(self) -> str:
		hours, rem = divmod(self.duration.seconds, 3600)
		minutes = "{:02}".format(rem // 60) if rem // 60 else ""
		return "{}h{}".format(hours, minutes)

	@property
	def pretty_type(self) -> str:
		type = self.Types(self.act_type).label
		return type
		# status = self.Status(self.status)
		# status_repr = "présentiel ou distanciel"
		# if status == self.Status.DISTANT:
		# 	status_repr = "distanciel"
		# elif status == self.Status.PRESENT:
		# 	status_repr = "présentiel"
		# return "{} ({})".format(type, status_repr)

	@property
	def slug(self) -> str:
		"""Returns the planning/display slug for this activity"""
		return "act-{}".format(self.id)

	@property
	def slots(self):
		"""Returns a list of slots related to self"""
		return SlotModel.objects.filter(activity=self, on_planning=True).order_by("start")

	def __str__(self):
		return self.title

	class Meta:
		verbose_name = "activité"


class SlotModel(models.Model):
	"""Crénaux indiquant ou une activité se place dans le planning
	Dans une table à part car un activité peut avoir plusieurs créneaux.
	Les inscriptions se font à des créneaux et non des activités"""

	TITLE_SPECIFIER = "{act_title}"

	activity = models.ForeignKey(ActivityModel, on_delete=models.CASCADE, verbose_name="Activité")
	title = models.CharField(
		"Titre", max_length=200, default=TITLE_SPECIFIER,
		help_text="Utilisez '{}' pour insérer le titre de l'activité correspondante".format(
			TITLE_SPECIFIER),
	)
	start = models.DateTimeField("début")
	duration = models.DurationField(
		"durée", blank=True, null=True,
		help_text="Format 00:00:00. Laisser vide pour prendre la durée de l'activité correspondante"
	)
	room = models.CharField("salle", max_length=100, null=True, blank=True)
	on_planning = models.BooleanField(
		"afficher sur le planning", default=False,
		help_text="Nécessite de salle et heure de début non vide",
	)
	subscribing_open = models.BooleanField("ouvert aux inscriptions", default=False,
		help_text="Si vrai, apparaît dans la liste du formulaire d'inscription"
	)
	color = models.CharField(
		"Couleur", choices=Colors.choices, max_length=1, default=Colors.DARK_BLUE,
		help_text="La légende des couleurs est modifiable dans les paramètres"
	)

	@property
	def participants(self):
		return ActivityChoicesModel.objects.filter(slot=self, accepted=True)

	@property
	def end(self):
		"""Heure de fin du créneau"""
		if self.duration:
			return self.start + self.duration
		return self.start + self.activity.duration

	def conflicts(self, other: "SlotModel") -> bool:
		"""Check whether these slots overlap"""
		if self.start <= other.start:
			return other.start <= self.end
		return self.start <= other.end

	@staticmethod
	def relative_day(date: datetime.datetime) -> int:
		"""Relative day to start.
		- friday   04:00 -> 03:59 = day 0
		- saturday 04:00 -> 03:59 = day 1
		- sunday   04:00 -> 03:59 = day 2
		returns 0 if no date_start is defined in settings"""
		settings = SiteSettings.load()
		if settings.date_start:
			return (date - timezone.datetime.combine(
				settings.date_start, datetime.time(hour=4), timezone.get_current_timezone()
			)).days
		else:
			return 0

	@staticmethod
	def fake_date(date: datetime.datetime):
		"""Fake day for display on the (single day planning)"""
		settings = SiteSettings.load()
		if settings.date_start:
			time = date.timetz()
			offset = datetime.timedelta(0)
			if time.hour < 4:
				offset = datetime.timedelta(days=1)
			return timezone.datetime.combine(
				settings.date_start + offset,
				date.timetz()
			)
		return None

	@property
	def start_day(self) -> int:
		"""returns a day (0-2)"""
		return self.relative_day(self.start)

	@property
	def end_day(self) -> int:
		"""returns a day (0-2)"""
		return self.relative_day(self.end)

	@property
	def planning_start(self) -> int:
		return self.fake_date(self.start)

	@property
	def planning_end(self) -> int:
		return self.fake_date(self.end)

	def __str__(self) -> str:
		return self.title.replace(self.TITLE_SPECIFIER, self.activity.title)

	class Meta:
		verbose_name = "créneau"
		verbose_name_plural = "créneaux"


class ParticipantModel(models.Model):
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

	# mug = models.BooleanField("commander une tasse", default=False)

	def __str__(self) -> str:
		school = self.ENS(self.school).label.replace("ENS ", "") if self.school else ""
		return "{} {} ({})".format(self.user.first_name, self.user.last_name, school)

	@property
	def nb_meals(self) -> int:
		return (
			self.meal_friday_evening + self.meal_saturday_evening + self.meal_saturday_midday +
			self.meal_saturday_morning + self.meal_sunday_midday + self.meal_sunday_morning
		)

	class Meta:
		verbose_name = "participant"


class ActivityChoicesModel(models.Model):
	"""liste d'activités souhaitée de chaque participant,
	avec un order de priorité"""
	priority = models.PositiveIntegerField("priorité")
	participant = models.ForeignKey(
		ParticipantModel, on_delete=models.CASCADE, verbose_name="participant",
	)
	slot = models.ForeignKey(
		SlotModel, on_delete=models.CASCADE, verbose_name="créneau",
	)
	accepted = models.BooleanField("Obtenue", default=False)

	class Meta:
		# couples uniques
		unique_together = (("priority", "participant"), ("participant", "slot"))
		ordering = ("participant", "priority")
		verbose_name = "choix d'activités"
		verbose_name_plural = "choix d'activités"

EmailUser.profile = property(lambda user: ParticipantModel.objects.get_or_create(user=user)[0])
