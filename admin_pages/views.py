from typing import Any, Dict, List, Optional, Tuple

from django import VERSION
from django.conf import settings
from django.contrib import messages
from django.core.mail import mail_admins, send_mass_mail
from django.db.models import Count
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.template.defaultfilters import date as django_date
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import FormView, RedirectView, TemplateView

from accounts.models import EmailUser
from admin_pages.forms import Recipients, SendEmailForm
from home import models
from home.views import get_planning_context
from interludes import settings as site_settings
from shared.views import CSVWriteView, SuperuserRequiredMixin
from site_settings.models import ENS, Colors, SiteSettings

# ==============================
# Main Admin views
# ==============================


class AdminView(SuperuserRequiredMixin, TemplateView):
    template_name = "admin.html"

    def get_metrics(self) -> Any:
        """Various metrics, return as a class"""
        registered = models.ParticipantModel.objects.filter(is_registered=True, user__is_active=True)
        acts = models.ActivityModel.objects.all()
        slots_in = models.SlotModel.objects.all()
        wishes = models.ActivityChoicesModel.objects.filter(
            participant__is_registered=True, participant__user__is_active=True
        )

        class metrics:
            participants = registered.count()
            ulm = registered.filter(school=ENS.ENS_ULM).count()
            lyon = registered.filter(school=ENS.ENS_LYON).count()
            rennes = registered.filter(school=ENS.ENS_RENNES).count()
            saclay = registered.filter(school=ENS.ENS_CACHAN).count()
            non_registered = EmailUser.objects.filter(is_active=True).count() - participants
            # mugs = registered.filter(mug=True).count()
            sleeps = registered.filter(sleeps=True).count()
            paid = registered.filter(paid=True).count()

            meal1 = registered.filter(meal_friday_evening=True).count()
            meal2 = registered.filter(meal_saturday_morning=True).count()
            meal3 = registered.filter(meal_saturday_midday=True).count()
            meal4 = registered.filter(meal_saturday_evening=True).count()
            meal5 = registered.filter(meal_sunday_morning=True).count()
            meal6 = registered.filter(meal_sunday_midday=True).count()
            meal7 = registered.filter(meal_sunday_evening=True).count()
            meals = meal1 + meal2 + meal3 + meal4 + meal5 + meal6

            activites = acts.count()
            displayed = acts.filter(display=True).count()
            act_ins = acts.filter(display=True, must_subscribe=True).count()
            communicate = acts.filter(communicate_participants=True).count()
            st_present = acts.filter(display=True, status=models.ActivityModel.Status.PRESENT).count()
            st_distant = acts.filter(display=True, status=models.ActivityModel.Status.DISTANT).count()
            st_both = acts.filter(display=True, status=models.ActivityModel.Status.BOTH).count()

            slots = slots_in.count()
            true_ins = slots_in.filter(subscribing_open=True).count()
            wish = wishes.count()
            granted = wishes.filter(accepted=True).count()
            malformed = models.ActivityChoicesModel.objects.filter(slot__subscribing_open=False).count()

            revenue = sum(x.cost() for x in registered)
            revenue_meal = sum(x.cost_meals() for x in registered)
            revenue_sleep = sum(x.cost_sleep() for x in registered)
            revenue_entry = sum(x.cost_entry() for x in registered)

        return metrics

    def url_parameters(self, field: Optional[str] = None) -> str:
        """URL de modification des paramètres"""
        url = reverse("admin:site_settings_sitesettings_change", args=[1])
        if field is not None:
            url += "#id_" + field
        return '<a href="{}">Modifier</a>'.format(url)

    def url_activity(
        self, activity: models.ActivityModel, field: Optional[str] = None, text: Optional[str] = None
    ) -> str:
        url = reverse("admin:home_activitymodel_change", args=[activity.id])
        if field is not None:
            url += "#id_" + field
        if text is None:
            text = str(activity.title)
        return '<a href="{}">{}</a>'.format(url, text)

    def url_slot(self, slot: models.SlotModel, field: Optional[str] = None) -> str:
        url = reverse("admin:home_slotmodel_change", args=[slot.id])
        if field is not None:
            url += "#id_" + field
        return '<a href="{}">{}</a>'.format(url, slot)

    def url_participant(self, participant: models.ParticipantModel, field: Optional[str] = None) -> str:
        url = reverse("admin:home_participantmodel_change", args=[participant.id])
        if field is not None:
            url += "#id_" + field
        return '<a href="{}">{}</a>'.format(url, participant)

    def url_user(self, user: EmailUser, field: Optional[str] = None) -> str:
        url = reverse("admin:accounts_emailuser_change", args=[user.id])
        if field is not None:
            url += "#id_" + field
        return '<a href="{}">{}</a>'.format(url, user.email)

    def url_add_slot(self, activity: models.ActivityModel) -> str:
        url = reverse("admin:home_slotmodel_add")
        return '<a href="{}?activity={}">nouveau créneau</a>'.format(url, activity.id)

    def format_ok(self, message: str) -> str:
        """Mise en forme d'un check passé avec succès"""
        return '<li class="success">' + message + "</li>"

    def format_error(self, message: str, errors: Optional[List[str]] = None) -> str:
        """Mise en forme d'un check qui échoue"""
        if errors is not None:
            for err in errors:
                message += "<br> &bullet;&ensp; " + err
        return '<li class="error">' + message + "</li>"

    def check_activity_slots(self) -> str:
        """Vérification du planning et de la répartition des activités:
        verifie que toutes les activité demandant une liste de participant ont un créneaux"""
        activities = models.ActivityModel.objects.filter(display=True, communicate_participants=True)
        errors = []
        for activity in activities:
            count = models.SlotModel.objects.filter(activity=activity).count()
            if count == 0:
                errors.append("{} (créer un {})".format(self.url_activity(activity), self.url_add_slot(activity)))
        if errors:
            return self.format_error(
                "Certaines activités demandant une liste de participants n'ont pas de créneaux, leurs orgas vont recevoir un mail inutile.",
                errors,
            )
        return self.format_ok("Toutes les activités demandant une liste de participants ont au moins un créneau")

    def check_hidden_activities(self) -> str:
        """Vérification du planning et de la répartition des activités:
        Vérifie que des activités ne soient pas masquées"""
        hidden_activites = models.ActivityModel.objects.filter(display=False)
        errors = []
        for act in hidden_activites:
            errors.append(self.url_activity(act, "display"))
        if errors:
            return self.format_error("Certaines activités ne sont pas affichées", errors)
        return self.format_ok("Toutes les activités sont affichées")

    def check_repartition_participant_nb(self) -> str:
        """Vérification de la répartition des activités:
        Vérifie que le nombre de participant inscrit
        à chaque activité est compris entre le min et le max"""
        slots = models.SlotModel.objects.filter(subscribing_open=True)
        min_fails = []
        max_fails = []
        for slot in slots:
            total = models.ActivityChoicesModel.objects.filter(
                slot=slot,
                accepted=True,
                participant__is_registered=True,
                participant__user__is_active=True,
            ).aggregate(total=Count("id"))["total"]
            max = slot.activity.max_participants
            min = slot.activity.min_participants
            if max != 0 and max < total:
                max_fails.append("{}: {} inscrits (maximum {})".format(self.url_slot(slot), total, max))
            if min > total:
                min_fails.append("{}: {} inscrits (minimum {})".format(self.url_slot(slot), total, min))
        message = ""
        if min_fails:
            message += self.format_error("Créneaux en sous-effectif&nbsp;:", min_fails)
        else:
            message += self.format_ok("Aucune créneau en sous-effectif")
        if max_fails:
            message += self.format_error("Créneaux en sur-effectif&nbsp;:", max_fails)
        else:
            message += self.format_ok("Aucune créneau en sur-effectif")
        return message

    Conflicts = List[Tuple[models.SlotModel, models.SlotModel]]

    def get_conflicts(self) -> Conflicts:
        """Returns a list of overlapping slot pairs"""
        slots = models.SlotModel.objects.filter(subscribing_open=True)
        conflicts = []
        for i, slot_1 in enumerate(slots):
            for slot_2 in slots[i + 1 :]:
                if slot_1.conflicts(slot_2):
                    conflicts.append((slot_1, slot_2))
        return conflicts

    def check_repartition_no_simultaneaous_inscriptions(self, conflicts: Conflicts) -> str:
        """Vérification de la répartition des activités:
        Vérifie que personne n'est inscrit à des activités simultanées
        Vérifie aussi que personne n'est inscrit en même temps qu'une activité qu'il organise"""

        base_qs = models.ActivityChoicesModel.objects.filter(
            accepted=True,
            participant__is_registered=True,
            participant__user__is_active=True,
        )
        errors = []
        errors_orga = []
        for slot_1, slot_2 in conflicts:
            participants_1 = {x.participant for x in base_qs.filter(slot=slot_1)}
            participants_2 = {x.participant for x in base_qs.filter(slot=slot_2)}
            intersection = participants_1.intersection(participants_2)
            if intersection:
                errors.append(
                    '{} participe à la fois à "{}" et à "{}"'.format(
                        ", ".join(self.url_participant(x) for x in intersection),
                        self.url_slot(slot_1),
                        self.url_slot(slot_2),
                    )
                )
            for participant in participants_1:
                if participant.user == slot_2.activity.host:
                    errors_orga.append(
                        "{} ({}) organise '{}' et participe à {}".format(
                            self.url_participant(participant),
                            self.url_user(participant.user),
                            self.url_slot(slot_2),
                            self.url_slot(slot_1),
                        )
                    )
            for participant in participants_2:
                if participant.user == slot_1.activity.host:
                    errors_orga.append(
                        "{} ({}) organise '{}' et participe à {}".format(
                            self.url_participant(participant),
                            self.url_user(participant.user),
                            self.url_slot(slot_2),
                            self.url_slot(slot_1),
                        )
                    )

        result = ""
        if errors:
            result += self.format_error("Des participants ont plusieurs créneaux au même moment&nbsp;:", errors)
        else:
            result += self.format_ok("Aucun inscrit à plusieurs créneaux simultanées")
        if errors_orga:
            errors_orga = list(set(errors_orga))  # Ugly way to avoid duplicate warnings
            return result + self.format_error(
                "Certains orgas sont incrit à des activités se déroulant en même temps que celle qu'ils organisent&nbsp;:",
                errors_orga,
            )
        return result + self.format_ok(
            "Aucun orga n'est incrit à une activité en même temps que celle qu'il organise<br>"
            "(Ne compare que les orgas principaux, pas les éventuels additionels)"
        )

    def check_repartition_no_duplicate_inscription(self) -> str:
        """Vérification de la répartition des activités:
        vérifie que personne n'est inscrit à la même activité plusieurs fois"""
        slots = models.SlotModel.objects.filter(subscribing_open=True)
        conflicts = []
        for i, slot_1 in enumerate(slots):
            for slot_2 in slots[i + 1 :]:
                if slot_1.activity == slot_2.activity:
                    conflicts.append((slot_1, slot_2))
        base_qs = models.ActivityChoicesModel.objects.filter(
            accepted=True,
            participant__is_registered=True,
            participant__user__is_active=True,
        )
        errors = []
        for slot_1, slot_2 in conflicts:
            participants_1 = {x.participant for x in base_qs.filter(slot=slot_1)}
            participants_2 = {x.participant for x in base_qs.filter(slot=slot_2)}
            intersection = participants_1.intersection(participants_2)
            if intersection:
                errors.append(
                    '{} inscrit aux créneaux "{}" et  "{}" de l\'activité "{}"'.format(
                        ", ".join(self.url_participant(x) for x in intersection),
                        self.url_slot(slot_1),
                        self.url_slot(slot_2),
                        self.url_activity(slot_1.activity),
                    )
                )

        if errors:
            return self.format_error("Des participants sont inscrits plusieurs fois à la même activité&nbsp;:", errors)
        return self.format_ok("Aucun inscrit plusieurs fois à une même activité")

    def check_planning_slots_nb(self) -> str:
        """Vérification du planning:
        Vérifie que toutes les activités ont le bon nombre de créneaux
        dans le planning"""
        errors = []
        activities = models.ActivityModel.objects.filter(display=True)
        for activity in activities:
            nb_wanted = activity.desired_slot_nb
            nb_got = activity.slots().count()
            if nb_wanted != nb_got:
                errors.append(
                    '"{}" souhaite {} crénaux mais en a {} ({}).'.format(
                        self.url_activity(activity), nb_wanted, nb_got, self.url_add_slot(activity)
                    )
                )
        if errors:
            return self.format_error("Certaines activités ont trop/pas assez de crénaux&nbsp;:", errors)
        return self.format_ok("Toutes les activités (affichées) ont le bon nombre de crénaux")

    def check_planning_registration_matches(self) -> str:
        """Vérification du planning:
        Vérifie que les créneaux sur inscription correspondent aux activités
        sur inscription"""
        errors = []
        activities = models.ActivityModel.objects.filter(display=True)
        for activity in activities:
            for slot in activity.slots():
                if slot.subscribing_open != activity.must_subscribe:
                    if slot.subscribing_open:
                        errors.append(
                            "Le créneau '{}' est 'sur inscription', mais son activité correspondante '{}' ne l'est pas".format(
                                self.url_slot(slot, "subscribing_open"), self.url_activity(activity, "must_subscribe")
                            )
                        )
                    else:
                        errors.append(
                            "L'activité '{}' est 'sur inscription', mais son créneau '{}' ne l'est pas".format(
                                self.url_activity(activity, "must_subscribe"), self.url_slot(slot, "subscribing_open")
                            )
                        )
        if errors:
            return self.format_error(
                'Les cases "sur inscription" ne correspondent pas entre activités et créneaux&nbsp;:', errors
            )
        return self.format_ok(
            'Toutes les activités (affichées) "sur inscription" n\'ont que des créneaux sur inscription (et réciproquement)'
        )

    def check_planning_slot_conflicts(self, conflicts: Conflicts) -> str:
        """Vérification du planning:
        Vérifie qu'il n'y a pas d'orga gérant plusieurs activités simultanément"""
        errors = []
        for slot1, slot2 in conflicts:
            conflict_text = "'{}' (le {} UTC) et '{}' (le {} UTC)".format(
                self.url_slot(slot1),
                django_date(slot1.start, "l à H:i"),
                self.url_slot(slot2),
                django_date(slot2.start, "l à H:i"),
            )
            if slot1.activity.host is not None and slot1.activity.host == slot2.activity.host:
                errors.append(
                    "L'utilisateur '{}' organise {}".format(self.url_user(slot1.activity.host), conflict_text)
                )
            elif slot1.activity.host_name is not None and slot1.activity.host_name == slot2.activity.host_name:
                errors.append("'{}' organise {}".format(slot1.activity.host_name, conflict_text))
            elif slot1.activity.host_email == slot2.activity.host_email:
                errors.append("'{}' organise {}".format(slot1.activity.host_email, conflict_text))
        if errors:
            return self.format_error("Certains organisteurs gèrent plusieurs créneaux simultanément&nbsp;:", errors)
        return self.format_ok(
            "Aucun organisateur ne gèrent de créneaux simultanés.<br>(Ne compare que les orgas principaux, pas les éventuels additionels)"
        )

    def validate_activity_allocation(self) -> Dict[str, Any]:
        settings = SiteSettings.load()
        validations = '<ul class="messagelist">'

        # validate global settings
        if not settings.inscriptions_open:
            validations += self.format_ok("Les inscriptions sont fermées")
        else:
            validations += self.format_error(
                "Les inscriptions sont encores ouvertes ({})".format(self.url_parameters("inscriptions_open"))
            )
        if settings.activities_allocated:
            validations += self.format_ok("La répartition est marquée comme effectuée")
        else:
            validations += self.format_error(
                "La répartition n'est pas marquée comme effectuée ({})".format(
                    self.url_parameters("activities_allocated")
                )
            )

        conflicts = self.get_conflicts()

        # longer validations
        hidden = self.check_hidden_activities()
        validations += hidden
        validations += self.check_activity_slots()
        validations += self.check_repartition_participant_nb()
        validations += self.check_repartition_no_simultaneaous_inscriptions(conflicts)
        validations += self.check_repartition_no_duplicate_inscription()

        if settings.discord_link:
            validations += self.format_ok("Le lien du discord est renseigné")
        else:
            validations += self.format_error(
                "Le lien du discord n'est pas renseigné ({})".format(self.url_parameters("discord_link"))
            )

        validations += "</ul>"

        user_email_nb = models.ParticipantModel.objects.filter(is_registered=True, user__is_active=True).count()
        acts = models.ActivityModel.objects.filter(display=True)
        orga_planning_email_nb = len(set(x.host_email for x in acts))
        orga_email_nb = len(set(x.host_email for x in acts.filter(communicate_participants=True)))

        planning_validations = ""
        if settings.display_planning:
            planning_validations += self.format_ok("Le planning est affiché")
        else:
            planning_validations += self.format_error(
                "Le planning n'est pas affiché ({})".format(self.url_parameters("display_planning"))
            )
        planning_validations += hidden
        planning_validations += self.check_planning_slots_nb()
        planning_validations += self.check_planning_registration_matches()
        planning_validations += self.check_planning_slot_conflicts(conflicts)

        return {
            "django_version": VERSION,
            "validations": validations,
            "user_email_nb": user_email_nb,
            "orga_planning_email_nb": orga_planning_email_nb,
            "orga_email_nb": orga_email_nb,
            "validation_errors": '<li class="error">' in validations,
            "planning_validation": planning_validations,
            "planning_validation_errors": '<li class="error">' in planning_validations,
        }

    def get_context_data(self, *args, **kwargs) -> Dict[str, str]:
        context = super().get_context_data(*args, **kwargs)
        context["metrics"] = self.get_metrics()
        context.update(get_planning_context())
        context.update(self.validate_activity_allocation())
        return context


# ==============================
# DB Export Views
# ==============================


class ExportActivities(SuperuserRequiredMixin, CSVWriteView):
    filename = "activites_interludes"
    model = models.ActivityModel
    fields = [
        # The key is "host_id" but listed as "host" in auto-found field names
        # which leads to an error...
        "id",
        "display",
        "title",
        "act_type",
        "game_type",
        "description",
        "desc_as_html",
        "host_id",
        "host_name",
        "host_email",
        "host_info",
        "show_email",
        "must_subscribe",
        "communicate_participants",
        "max_participants",
        "min_participants",
        "duration",
        "desired_slot_nb",
        "available_friday_evening",
        "available_friday_night",
        "available_saturday_morning",
        "available_saturday_afternoon",
        "available_saturday_evening",
        "available_saturday_night",
        "available_sunday_morning",
        "available_sunday_afternoon",
        "constraints",
        "status",
        "needs",
        "comments",
    ]


class ExportSlots(SuperuserRequiredMixin, CSVWriteView):
    filename = "créneaux_interludes"
    headers = [
        "Titre",
        "Début",
        "Salle",
        "Ouverte aux inscriptions",
        "Affiché sur le planning",
        "Affiché sur l'activité",
        "Couleur",
        "Durée",
        "Durée activité",
    ]

    def get_rows(self):
        slots = models.SlotModel.objects.all()
        rows = []
        for slot in slots:
            rows.append(
                [
                    str(slot),
                    slot.start,
                    slot.room,
                    slot.subscribing_open,
                    slot.on_planning,
                    slot.on_activity,
                    Colors(slot.color).name,
                    slot.duration,
                    slot.activity.duration,
                ]
            )
        return rows


class ExportParticipants(SuperuserRequiredMixin, CSVWriteView):
    school: Optional[ENS] = None
    filename = "participants_interludes"
    headers = [
        "id",
        "mail",
        "prénom",
        "nom",
        "ENS",
        "Dors sur place",  # "Tasse",
        "Nombre de repas",
        "Repas vendredi",
        "Repas S matin",
        "Repas S midi",
        "Repas S soir",
        "Repas D matin",
        "Repas D midi",
        "Reaps D soir",
        "Salarié",
        "Tarif",
        "Montant payé",
        "Nombre murders",
        "Autre contact",
        "Commentaires murders",
        "Commentaires",
        "Compte clipper",
    ]

    def get_filename(self):
        if self.school is None:
            return super().get_filename()
        return "participants_" + self.school.label.lower().replace(" ", "_").replace("ens_", "")

    def get_rows(self):
        profiles = models.ParticipantModel.objects.filter(is_registered=True, user__is_active=True)
        if self.school is not None:
            profiles = profiles.filter(school=self.school)
        rows = []
        for profile in profiles:
            rows.append(
                [
                    profile.user.id,
                    profile.user.email,
                    profile.user.first_name,
                    profile.user.last_name,
                    profile.get_school_display(),
                    profile.sleeps,
                    # profile.mug,
                    profile.nb_meals(),
                    profile.meal_friday_evening,
                    profile.meal_saturday_morning,
                    profile.meal_saturday_midday,
                    profile.meal_saturday_evening,
                    profile.meal_sunday_morning,
                    profile.meal_sunday_midday,
                    profile.meal_sunday_evening,
                    profile.paid,
                    profile.cost(),
                    profile.amount_paid,
                    profile.nb_murder,
                    profile.extra_contact,
                    profile.murder_comment,
                    profile.comment,
                    hasattr(profile.user, "clipper_account"),
                ]
            )
        rows.sort(key=lambda x: (x[4], x[3], x[2]))  # sort by school, last_name, first_name
        return rows


class ExportActivityChoices(SuperuserRequiredMixin, CSVWriteView):
    filename = "choix_activite_interludes"
    model = models.ActivityChoicesModel
    headers = [
        "id_participant",
        "nom_participant",
        "mail_participant",
        "priorité",
        "obtenu",
        "nom_créneau",
        "id_créneau",
    ]

    def get_rows(self):
        activities = models.ActivityChoicesModel.objects.all()
        rows = []
        for act in activities:
            if act.participant.is_registered and act.participant.user.is_active:
                rows.append(
                    [
                        act.participant.id,
                        str(act.participant),
                        act.participant.user.email,
                        act.priority,
                        act.accepted,
                        str(act.slot),
                        act.slot.id,
                    ]
                )
        return rows


# ==============================
# Send email views
# ==============================


class SendEmailBase(SuperuserRequiredMixin, RedirectView):
    """Classe abstraite pour l'envoie d'un groupe d'emails"""

    pattern_name = "admin_pages:index"
    from_address: Optional[str] = None  # defaults to DEFAULT_FROM_EMAIL setting

    def send_emails(self) -> None:
        raise NotImplementedError("{}.send_emails isn't implemented".format(self.__class__.__name__))

    def get_redirect_url(self, *args, **kwargs):
        settings = SiteSettings.load()
        if settings.allow_mass_mail:
            self.send_emails()
        else:
            messages.error(self.request, "L'envoi de mail de masse est désactivé dans les réglages")
        return reverse(self.pattern_name)


# Subject, Message, From, To
EMAIL = Tuple[str, str, Optional[str], List[str]]


class SendUserEmail(SendEmailBase):
    """Envoie aux utilisateurs leur repartition d'activité"""

    def get_emails(self) -> List[EMAIL]:
        """genere les mails a envoyer"""
        participants = models.ParticipantModel.objects.filter(is_registered=True, user__is_active=True)
        emails = []
        settings = SiteSettings.load()
        for participant in participants:
            my_choices = models.ActivityChoicesModel.objects.filter(participant=participant)
            message: str = render_to_string(
                "email/user.html",
                {
                    "user": participant.user,
                    "settings": settings,
                    "requested_activities_nb": my_choices.count(),
                    "my_choices": my_choices.filter(accepted=True),
                },
            )
            emails.append(
                (
                    site_settings.USER_EMAIL_SUBJECT_PREFIX + "Vos activités",  # subject
                    message,
                    self.from_address,  # From:
                    [participant.user.email],  # To:
                )
            )
        return emails

    def send_emails(self) -> None:
        settings = SiteSettings.load()
        if settings.user_notified:
            messages.error(
                self.request,
                "Les participants ont déjà reçu un mail annonçant la répartition. Modifiez les réglages pour en envoyer un autre",
            )
            return
        settings.user_notified = now()
        settings.save()
        emails = self.get_emails()

        nb_sent = send_mass_mail(emails, fail_silently=False)
        mail_admins(
            "Emails de répartition envoyés aux participants",
            "Les participants ont reçu un mail leur communiquant la répartition des activités\n"
            "Nombre total de mail envoyés: {}\n\n"
            "{}".format(nb_sent, site_settings.EMAIL_SIGNATURE),
        )
        messages.success(self.request, "{} mails envoyés aux utilisateurs".format(nb_sent))


class SendOrgaEmail(SendEmailBase):
    """
    Envoie aux organisateur leur communiquant les nom/mail des inscrits
    à leurs activités
    """

    def get_emails(self) -> List[EMAIL]:
        """genere les mails a envoyer"""
        activities = models.ActivityModel.objects.filter(display=True, communicate_participants=True)
        emails = []
        settings = SiteSettings.load()
        seen = set()
        for activity in activities:
            # To avoid sending too many email, all activities with the same
            # host_email get sent in a single email.
            if activity.host_email in seen:
                continue
            seen.add(activity.host_email)
            message: str = render_to_string(
                "email/orga.html",
                {
                    "activities": activities.filter(host_email=activity.host_email),
                    "settings": settings,
                },
            )
            emails.append(
                (
                    site_settings.USER_EMAIL_SUBJECT_PREFIX + "Liste d'inscrits à vos activités",  # subject
                    message,
                    self.from_address,  # From:
                    [activity.host_email],  # To:
                )
            )
        return emails

    def send_emails(self) -> None:
        settings = SiteSettings.load()
        if settings.orga_notified:
            messages.error(
                self.request,
                "Les orgas ont déjà reçu un mail avec leur listes d'inscrits. Modifiez les réglages pour en envoyer un autre",
            )
            return
        settings.orga_notified = now()
        settings.save()
        emails = self.get_emails()

        nb_sent = send_mass_mail(emails, fail_silently=False)
        mail_admins(
            "Listes d'inscrits envoyés aux orgas",
            "Les mails communiquant aux organisateurs leur listes d'inscrit ont été envoyés\n"
            "Nombre total de mail envoyés: {}\n\n"
            "{}".format(nb_sent, site_settings.EMAIL_SIGNATURE),
        )
        messages.success(self.request, "{} mails envoyés aux orgas".format(nb_sent))


class SendOrgaPlanningEmail(SendEmailBase):
    """
    Envoie aux organisateur leur communiquant les créneaux de leurs activités
    """

    def get_emails(self) -> List[EMAIL]:
        """genere les mails a envoyer"""
        activities = models.ActivityModel.objects.filter(display=True)
        emails = []
        settings = SiteSettings.load()
        seen = set()
        for activity in activities:
            # To avoid sending too many email, all activities with the same
            # host_email get sent in a single email.
            if activity.host_email in seen:
                continue
            seen.add(activity.host_email)
            message: str = render_to_string(
                "email/orga_planning.html",
                {
                    "activities": activities.filter(host_email=activity.host_email),
                    "settings": settings,
                },
            )
            emails.append(
                (
                    site_settings.USER_EMAIL_SUBJECT_PREFIX + "Planning interludes",  # subject
                    message,
                    self.from_address,  # From:
                    [activity.host_email],  # To:
                )
            )
        return emails

    def send_emails(self) -> None:
        settings = SiteSettings.load()
        if settings.orga_planning_notified:
            messages.error(
                self.request,
                "Les orgas ont déjà reçu un mail avec leur créneaux. Modifiez les réglages pour en envoyer un autre",
            )
            return
        settings.orga_planning_notified = now()
        settings.save()
        emails = self.get_emails()

        nb_sent = send_mass_mail(emails, fail_silently=False)
        mail_admins(
            "Créneaux envoyés aux organisateurs d'activités",
            "Les mails communiquant aux organisateurs les créneaux de leurs activités ont été envoyés.\n"
            "Nombre total de mail envoyés: {}\n\n"
            "{}".format(nb_sent, site_settings.EMAIL_SIGNATURE),
        )
        messages.success(self.request, "{} mails envoyés aux orgas".format(nb_sent))


class NewEmail(SuperuserRequiredMixin, FormView):
    """Créer un nouveau mail"""

    template_name = "send_email.html"
    form_class = SendEmailForm
    success_url = reverse_lazy("admin_pages:index")
    from_address: Optional[str] = None

    def get_emails(self, selection: Recipients) -> List[str]:
        """return the list of destination emails"""
        if selection == Recipients.ALL:
            users = EmailUser.objects.filter(is_active=True)
            return [u.email for u in users]
        elif selection == Recipients.REGISTERED:
            participants = models.ParticipantModel.objects.filter(is_registered=True, user__is_active=True)
            return [p.user.email for p in participants]
        elif selection == Recipients.ULMITES:
            participants = models.ParticipantModel.objects.filter(
                is_registered=True, user__is_active=True, school=ENS.ENS_ULM
            )
            return [p.user.email for p in participants]
        elif selection == Recipients.LYONNAIS:
            participants = models.ParticipantModel.objects.filter(
                is_registered=True, user__is_active=True, school=ENS.ENS_LYON
            )
            return [p.user.email for p in participants]
        elif selection == Recipients.RENNAIS:
            participants = models.ParticipantModel.objects.filter(
                is_registered=True, user__is_active=True, school=ENS.ENS_RENNES
            )
            return [p.user.email for p in participants]
        elif selection == Recipients.CACHANAIS:
            participants = models.ParticipantModel.objects.filter(
                is_registered=True, user__is_active=True, school=ENS.ENS_CACHAN
            )
            return [p.user.email for p in participants]
        elif selection == Recipients.ORGAS:
            activities = models.ActivityModel.objects.filter(display=True)
            return [a.host_email for a in activities]
        else:
            raise ValueError("Invalid selection specifier\n")

    @staticmethod
    def sending_allowed() -> bool:
        """Checks if sending mass emails is allowed"""
        settings = SiteSettings.load()
        return settings.allow_mass_mail

    def form_valid(self, form: SendEmailForm) -> HttpResponse:
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if not self.sending_allowed():
            messages.error(self.request, "L'envoi de mail de masse est désactivé dans les réglages")
        else:
            dest = form.cleaned_data["dest"]
            subject = form.cleaned_data["subject"]
            text = form.cleaned_data["text"]
            emails = []
            # Use a set to avoid possible duplications
            for to_addr in set(self.get_emails(dest)):
                emails.append([subject, text, self.from_address, [to_addr]])
            nb_sent = send_mass_mail(emails, fail_silently=False)  # type: ignore
            mail_admins(
                "Email envoyé",
                "Un email a été envoyé à {}.\n"
                "Nombre total de mail envoyés: {}\n\n"
                "Sujet : {}\n\n"
                "{}\n\n"
                "{}".format(
                    Recipients(dest).label,
                    nb_sent,
                    subject,
                    text,
                    site_settings.EMAIL_SIGNATURE,
                ),
            )
            messages.success(self.request, "{} mails envoyés".format(nb_sent))
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs) -> Dict[str, Any]:
        """ajoute l'email d'envoie aux données contextuelles"""
        context = super().get_context_data(*args, **kwargs)
        context["from_email"] = self.from_address if self.from_address else settings.DEFAULT_FROM_EMAIL
        participants = models.ParticipantModel.objects.filter(is_registered=True, user__is_active=True)
        context["registered_nb"] = participants.count()
        context["ulm"] = participants.filter(school=ENS.ENS_ULM).count()
        context["lyon"] = participants.filter(school=ENS.ENS_LYON).count()
        context["rennes"] = participants.filter(school=ENS.ENS_RENNES).count()
        context["saclay"] = participants.filter(school=ENS.ENS_CACHAN).count()
        context["accounts_nb"] = EmailUser.objects.filter(is_active=True).count()
        return context

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if self.sending_allowed():
            return super().get(request, *args, **kwargs)
        messages.error(request, "L'envoi de mail de masse est désactivé dans les réglages")
        return HttpResponseRedirect(self.get_success_url())


class SiteInfo(SuperuserRequiredMixin, TemplateView):
    template_name = "info.html"
