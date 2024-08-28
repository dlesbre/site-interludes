from authens.models import User
from django import VERSION
from django.conf import settings
from django.contrib import messages
from django.core.mail import mail_admins, send_mass_mail
from django.http import HttpResponseRedirect
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

    def validate_hidden_activities(self) -> str:
        """Vérifie que des activités ne soient pas masquées"""
        year = models.get_year()
        hidden_activites = models.ActivityModel.objects.filter(display=False, year=year)
        errors = ""
        for act in hidden_activites:
            errors += "<br> &bullet; &ensp; {}".format(act)
        if errors:
            return '<li class="error">Certaines activités ne sont pas affichées&nbsp;:{}</li>'.format(errors)
        return '<li class="success">Toutes les activités sont affichées</li>'

    def planning_validation(self):
        """Vérifie que toutes les activités ont le bon nombre de créneaux
        dans le planning"""
        errors = ""
        year = models.get_year()
        activities = models.ActivityModel.objects.filter(year=year)
        for activity in activities:
            nb_wanted = activity.desired_slot_nb
            nb_got = activity.slots.count()
            if nb_wanted != nb_got:
                errors += '<br> &bullet;&ensp; "{}" souhaite {} crénaux mais en a {}.'.format(
                    activity.title, nb_wanted, nb_got
                )
        if errors:
            return '<li class="error">Certaines activités ont trop/pas assez de crénaux :{}</li>'.format(errors)
        return '<li class="success">Toutes les activités ont le bon nombre de crénaux</li>'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["django_version"] = VERSION
        context["metrics"] = self.get_metrics()
        context["planning_validation"] = self.validate_hidden_activities() + self.planning_validation()
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
