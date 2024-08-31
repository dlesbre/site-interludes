from typing import List, Optional, Tuple

from authens.models import User
from django import VERSION
from django.conf import settings
from django.contrib import messages
from django.core.mail import mail_admins, send_mass_mail
from django.http import HttpResponseRedirect
from django.template.defaultfilters import date as django_date
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from admin_pages.forms import SendEmailForm
from home import models
from home.views import get_planning_context
from shared.views import CSVWriteView, SuperuserRequiredMixin
from site_settings.models import Colors, SiteSettings

# ==============================
# Main Admin views
# ==============================


class AdminView(SuperuserRequiredMixin, TemplateView):
    template_name = "admin.html"

    def get_metrics(self):
        year = models.get_year()
        acts = models.ActivityModel.objects.filter(year=year)
        slots_in = models.SlotModel.objects.filter(activity__year=year)

        class metrics:
            users = User.objects.filter(is_active=True).count()

            activites = acts.count()
            displayed = acts.filter(display=True).count()
            act_ins = acts.filter(display=True, must_subscribe=True).count()

            slots = slots_in.count()

        return metrics

    def format_ok(self, message: str) -> str:
        """Mise en forme d'un check passé avec succès"""
        return '<li class="success">' + message + "</li>"

    def format_error(self, message: str, errors: Optional[List[str]] = None) -> str:
        """Mise en forme d'un check qui échoue"""
        if errors is not None:
            for err in errors:
                message += "<br> &bullet;&ensp; " + err
        return '<li class="error">' + message + "</li>"

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

    def check_hidden_activities(self) -> str:
        """Vérification du planning et de la répartition des activités:
        Vérifie que des activités ne soient pas masquées"""
        year = models.get_year()
        hidden_activites = models.ActivityModel.objects.filter(display=False, year=year)
        errors = []
        for act in hidden_activites:
            errors.append("{}".format(act))
        if errors:
            return self.format_error("Certaines activités ne sont pas affichées&nbsp;:", errors)
        return self.format_ok("Toutes les activités sont affichées")

    def check_planning_slots_nb(self) -> str:
        """Vérification du planning:
        Vérifie que toutes les activités ont le bon nombre de créneaux
        dans le planning"""
        errors = []
        year = models.get_year()
        activities = models.ActivityModel.objects.filter(year=year)
        for activity in activities:
            nb_wanted = activity.desired_slot_nb
            nb_got = activity.slots.count()
            if nb_wanted != nb_got:
                errors.append('"{}" souhaite {} crénaux mais en a {}.'.format(activity.title, nb_wanted, nb_got))
        if errors:
            return self.format_error("Certaines activités ont trop/pas assez de crénaux&nbsp;:", errors)
        return self.format_ok("Toutes les activités ont le bon nombre de crénaux")

    def check_planning_slot_conflicts(self, conflicts: Conflicts) -> str:
        """Vérification du planning:
        Vérifie qu'il n'y a pas d'orga gérant plusieurs activités simultanément"""
        errors = []
        for slot1, slot2 in conflicts:
            conflict_text = "'{}' (le {} UTC) et '{}' (le {} UTC)".format(
                slot1, django_date(slot1.start, "l à H:i"), slot2, django_date(slot2.start, "l à H:i")
            )
            if slot1.activity.host is not None and slot1.activity.host == slot2.activity.host:
                errors.append("L'utilisateur '{}' organise {}".format(slot1.activity.host, conflict_text))
            elif slot1.activity.host_name is not None and slot1.activity.host_name == slot2.activity.host_name:
                errors.append("'{}' organise {}".format(slot1.activity.host_name, conflict_text))
            elif slot1.activity.host_email == slot2.activity.host_email:
                errors.append("'{}' organise {}".format(slot1.activity.host_email, conflict_text))
        if errors:
            return self.format_error("Certains organisteurs gèrent plusieurs créneaux simultanément&nbsp;:", errors)
        return self.format_ok(
            "Aucun organisateur ne gèrent de créneaux simultanés.<br>(Ne compare que les orgas principaux, pas les éventuels additionels)"
        )

    def get_context_data(self, *args, **kwargs):
        conflicts = self.get_conflicts()

        planning_validations = ""
        if settings.display_planning:
            planning_validations += self.format_ok("Le planning est affiché")
        else:
            planning_validations += self.format_error("Le planning n'est pas affiché")
        planning_validations += self.check_hidden_activities()
        planning_validations += self.check_planning_slots_nb()
        planning_validations += self.check_planning_slot_conflicts(conflicts)

        context = super().get_context_data(*args, **kwargs)
        context["django_version"] = VERSION
        context["metrics"] = self.get_metrics()
        context["planning_validation"] = planning_validations
        context["planning_validation_errors"] = '<li class="error">' in planning_validations
        context.update(get_planning_context())
        return context


# ==============================
# DB Export Views
# ==============================


class ExportActivities(SuperuserRequiredMixin, CSVWriteView):
    filename = "activites_48h"
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
        "needs",
        "comments",
    ]


class ExportSlots(SuperuserRequiredMixin, CSVWriteView):
    filename = "créneaux_48h"
    headers = [
        "Titre",
        "Début",
        "Salle",
        "Affiché sur le planning",
        "Affiché sur l'activité" "Couleur",
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
                    slot.on_planning,
                    slot.on_activity,
                    Colors(slot.color).name,
                    slot.duration,
                    slot.activity.duration,
                ]
            )
        return rows


# ==============================
# Send email views
# ==============================


class NewEmail(SuperuserRequiredMixin, FormView):
    """Créer un nouveau mail"""

    template_name = "send_email.html"
    form_class = SendEmailForm
    success_url = reverse_lazy("admin_pages:index")
    from_address = None

    def get_emails(self):
        """return the list of destination emails"""
        users = User.objects.filter(is_active=True)
        return [u.email for u in users]

    @staticmethod
    def sending_allowed():
        """Checks if sending mass emails is allowed"""
        settings = SiteSettings.load()
        return settings.allow_mass_mail

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        if not self.sending_allowed():
            messages.error(self.request, "L'envoi de mail de masse est désactivé dans les réglages")
        else:
            subject = form.cleaned_data["subject"]
            text = form.cleaned_data["text"]
            emails = []
            for to_addr in self.get_emails():
                emails.append([subject, text, self.from_address, [to_addr]])
            nb_sent = send_mass_mail(emails, fail_silently=False)
            mail_admins(
                "Email envoyé",
                "Un email a été envoyé à tous les utilisateurs.\n"
                "Nombre total de mail envoyés: {}\n\n"
                "Sujet : {}\n\n"
                "{}\n\n"
                "{}".format(
                    nb_sent,
                    subject,
                    text,
                    settings.EMAIL_SIGNATURE,
                ),
            )
            messages.success(self.request, "{} mails envoyés".format(nb_sent))
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        """ajoute l'email d'envoie aux données contextuelles"""
        context = super().get_context_data(*args, **kwargs)
        context["from_email"] = self.from_address if self.from_address else settings.DEFAULT_FROM_EMAIL
        context["accounts_nb"] = User.objects.filter(is_active=True).count()
        return context

    def get(self, request, *args, **kwargs):
        if self.sending_allowed():
            return super().get(request, *args, **kwargs)
        messages.error(request, "L'envoi de mail de masse est désactivé dans les réglages")
        return HttpResponseRedirect(self.get_success_url())


class SiteInfo(SuperuserRequiredMixin, TemplateView):
    template_name = "info.html"
