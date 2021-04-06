from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import EmailUser

class InterludesActivity(models.Model):
	"""une activité des interludes (i.e. JDR, murder)..."""

	class Status(models.TextChoices):
		"""en presentiel ou non"""
		PRESENT = "P", _("En présentiel uniquement")
		DISTANT = "D", _("En distanciel uniquement")
		BOTH = "2", _("Les deux")

	class Types(models.TextChoices):
		"""types d'activités"""
		TOURNAMENT = "Tournoi", _("Tournoi")
		GAME = "partie", _("Une partie")
		GAMES = "parties", _("Quelques parties")
		FREEPLAY = "freeplay", _("Freeplay")
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

	title = models.CharField("Titre", max_length=200)

	status = models.CharField("Présentiel/distanciel", choices=Status.choices, max_length=1)
	act_type = models.CharField("Type", choices=Types.choices, max_length=12)

	duration = models.DurationField("Durée", help_text="format hh:mm:ss")
	max_participants = models.PositiveIntegerField(
		"Nombre maximum de participants", help_text="0 pour illimité"
	)
	min_participants = models.PositiveIntegerField(
		"Nombre minimum de participants"
	)

	communicate_participants = models.BooleanField("communiquer la liste des participants à l'orga avant l'événement")
	display = models.BooleanField("afficher dans la liste", default=False,
		help_text="Si vrai, s'affiche sur la page activités"
	)
	must_subscribe = models.BooleanField("sur inscription", default=False,
		help_text="Informatif, il faut utiliser 'ouverte aux inscriptions' pour ajouter dans la liste d'inscription"
	)
	subscribing_open = models.BooleanField("ouverte aux inscriptions", default=False,
		help_text="Si vrai, apparaît dans la liste du formulaire d'inscription"
	)
	host_name = models.CharField("nom de l'organisateur", max_length=50)
	host_email = models.EmailField("email de l'organisateur")
	description = models.TextField(
		"description", max_length=2000,
		help_text='Texte ou html selon la valeur de "Description HTML".\n'
	)
	desc_as_html = models.BooleanField("Description au format HTML", default=False,
		help_text="Assurer vous que le texte est bien formaté, cette option peut casser la page activités."
	)

	on_planning = models.BooleanField(
		"afficher sur le planning", default=False,
		help_text="Nécessite de salle et heure de début non vide"
	)
	start = models.DateTimeField("début", null=True, blank=True)
	room = models.CharField("salle", max_length=100, null=True, blank=True)

	canonical = models.ForeignKey("self",
		on_delete=models.SET_NULL, null=True, blank=True,
		verbose_name="Représentant canonique",
		help_text="Si plusieurs copie d'une activité existe (pour plusieurs crénaux), "
			"et une seule est affichée, sélectionner là dans les copie pour réparer les liens "
			"du planning vers la description"
	)

	notes = models.TextField("Notes privées", max_length=2000, blank=True)

	@property
	def end(self):
		if (not self.start) or (not self.duration):
			return None
		return self.start + self.duration

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
		id = self.id
		if self.canonical:
			id = self.canonical.id
		return "act-{}".format(id)

	@property
	def times_and_places(self) -> str:
		"""Returns a list of start times and place related to self
		(check canonical links for multiple timetable,
		only displays if on_planning is true)"""
		objects = InterludesActivity.objects.filter(
			models.Q(id=self.id) | models.Q(canonical=self)
		).filter(on_planning=True).values("start", "room").order_by("start")
		return objects

	def conflicts(self, other: "InterludesActivity") -> bool:
		"""Check whether these activites overlap"""
		if self.end is None or other.end is None:
			return False
		if self.start <= other.start:
			return other.start <= self.end
		return self.start <= other.end

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
