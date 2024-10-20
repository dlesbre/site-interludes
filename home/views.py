from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.core.mail import send_mail
from django.forms import formset_factory
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBase
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, RedirectView, TemplateView, View

from accounts.models import EmailUser
from home import models
from home.forms import (
    ActivityForm,
    ActivitySubmissionForm,
    BaseActivityFormSet,
    InscriptionForm,
)
from interludes import settings as site_settings
from pages.models import HTMLPageModel
from site_settings.models import SiteSettings

# ==============================
# Site static pages
# ==============================
# Moved to pages/views.py


def get_planning_context() -> Dict[str, Any]:
    """Returns the context dict needed to display the planning"""
    settings = SiteSettings.load()
    context: Dict[str, Any] = dict()
    context["planning"] = models.SlotModel.objects.filter(on_planning=True).order_by("title")
    if settings.date_start is not None:
        context["friday"] = settings.date_start.day
        context["saturday"] = (settings.date_start + timedelta(days=1)).day
        context["sunday"] = (settings.date_start + timedelta(days=2)).day
    else:
        context["friday"] = 1
        context["saturday"] = 2
        context["sunday"] = 3
    return context


# ==============================
# Profile and registration
# ==============================


class ProfileView(LoginRequiredMixin, TemplateView):
    """Vue des actions de gestion de son profil"""

    template_name = "profile.html"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = SiteSettings.load()
        user = self.request.user
        assert isinstance(user, EmailUser)
        if settings.activities_allocated:
            my_choices = models.ActivityChoicesModel.objects.filter(participant=user.profile, accepted=True)
        else:
            my_choices = models.ActivityChoicesModel.objects.filter(participant=user.profile)

        context["my_choices"] = my_choices
        return context


class RegisterClosed(TemplateView):
    """Vue pour quand les inscriptions ne sont pas ouvertes"""

    template_name = "inscription/closed.html"


class RegisterSignIn(TemplateView):
    """Vue affichée quand les inscriptions sont ouverte mais
    l'utilisateur n'est pas connecté"""

    template_name = "inscription/signin.html"


class RegisterUpdateView(LoginRequiredMixin, TemplateView):
    """Vue pour s'inscrire et modifier son inscription"""

    template_name = "inscription/form.html"
    form_class = InscriptionForm
    formset_class = formset_factory(form=ActivityForm, extra=3, formset=BaseActivityFormSet)
    success_url = reverse_lazy("profile")

    @staticmethod
    def get_slots(
        participant: models.ParticipantModel,
    ) -> List[Dict[str, models.SlotModel]]:
        activities = models.ActivityChoicesModel.objects.filter(participant=participant).order_by("priority")
        return [{"slot": act.slot} for act in activities]

    @staticmethod
    def set_activities(participant: models.ParticipantModel, formset):
        # delete old activities
        models.ActivityChoicesModel.objects.filter(participant=participant).delete()

        priority = 0
        for form in formset:
            data = form.cleaned_data
            if data:
                slot = data["slot"]
                models.ActivityChoicesModel(priority=priority, participant=participant, slot=slot).save()
                priority += 1

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        assert isinstance(request.user, EmailUser)
        participant = request.user.profile
        slots = self.get_slots(participant)
        form = self.form_class(instance=participant)
        formset = self.formset_class(initial=slots)
        context = {"form": form, "formset": formset}
        return render(request, self.template_name, context)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        assert isinstance(request.user, EmailUser)
        settings = SiteSettings.load()
        form = self.form_class(request.POST, instance=request.user.profile)
        if settings.activity_inscriptions_open:  # meal + sleep + activities open
            formset = self.formset_class(request.POST)
            if not (form.is_valid() and formset.is_valid()):
                context = {"form": form, "formset": formset}
                return render(request, self.template_name, context)
            self.set_activities(request.user.profile, formset)

        else:  # only meal and sleep open
            if not form.is_valid():
                participant = request.user.profile
                slots = self.get_slots(participant)
                formset = self.formset_class(initial=slots)
                context = {"form": form, "formset": formset}
                return render(request, self.template_name, context)

        form.save()

        messages.success(request, "Votre inscription a bien été enregistrée")
        return redirect(self.success_url, permanent=False)


class RegisterView(View):
    """Vue pour l'inscription
    repartie sur les vue RegisterClosed, RegisterSignIn et RegisterUpdateView"""

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponseBase:
        settings = SiteSettings.load()
        if not settings.inscriptions_open:
            return RegisterClosed.as_view()(request)
        if not request.user.is_authenticated:
            return RegisterSignIn.as_view()(request)
        return RegisterUpdateView.as_view()(request)


class UnregisterView(LoginRequiredMixin, RedirectView):
    pattern_name = "profile"

    def get_redirect_url(self, *args, **kwargs) -> str:
        assert isinstance(self.request.user, EmailUser)
        participant = self.request.user.profile
        participant.is_registered = False
        participant.save()
        messages.success(self.request, "Vous avez été désinscrit")
        return reverse(self.pattern_name)


# ==============================
# Activity Submission Form
# ==============================


class ActivitySubmissionView(LoginRequiredMixin, FormView):
    """Vue pour proposer une activité"""

    template_name = "activity_submission.html"
    form_class = ActivitySubmissionForm
    success_url = reverse_lazy("profile")

    @staticmethod
    def submission_check() -> bool:
        """Vérifie si le formulaire est ouvert ou non"""
        settings = SiteSettings.load()
        return settings.activity_submission_open

    def get_initial(self) -> Dict[str, str]:
        init = super().get_initial()
        user = self.request.user
        assert isinstance(user, EmailUser)
        init.update(
            {
                "host_name": "{} {}".format(user.first_name, user.last_name),
                "host_email": user.email,
            }
        )
        return init

    def not_open(self, request: HttpRequest) -> HttpResponse:
        """Appelé quand le formulaire est désactivé"""
        messages.error(request, "La soumission d'activité est desactivée")
        return redirect(self.success_url, permanent=False)

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.submission_check():
            return self.not_open(request)
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not self.submission_check():
            return self.not_open(request)
        form = self.form_class(request.POST)
        if not form.is_valid():
            context = self.get_context_data()
            context["form"] = form
            return render(request, self.template_name, context)

        activity = form.save()
        activity.host = request.user
        activity.save()

        messages.success(
            request,
            "Votre activité a bien été enregistrée. Elle sera affichée sur le site après relecture par les admins.",
        )
        settings = SiteSettings.load()
        if settings.notify_on_activity_submission and settings.contact_email:
            message = render_to_string(
                "new_activity_email.txt",
                {
                    "user": request.user,
                    "request": request,
                    "activity": activity,
                    "signature": site_settings.EMAIL_SIGNATURE,
                },
            )
            send_mail(
                site_settings.USER_EMAIL_SUBJECT_PREFIX + "Nouvelle activité proposée",
                message,
                from_email=None,
                recipient_list=[settings.contact_email],
            )
        return redirect(self.success_url, permanent=False)


# ==============================
# Sitemap
# ==============================


ITEM = Tuple[str, Dict[str, str]]


class StaticViewSitemap(Sitemap):
    """Vue générant la sitemap.xml du site"""

    changefreq = "monthly"

    def items(self) -> List[ITEM]:
        """list of pages to appear in sitemap"""
        home: ITEM = "home", dict()
        inscription: ITEM = "inscription", dict()
        return [home, inscription] + [
            ("html_page", {"slug": obj.slug}) for obj in HTMLPageModel.objects.all() if obj.slug
        ]

    def location(self, item: ITEM) -> str:
        """real url of an item"""
        name, kwargs = item
        return reverse(name, kwargs=kwargs)

    def priority(self, obj: str) -> Optional[float]:
        """priority to appear in sitemap"""
        # Prioritize home page over the rest in search results
        if obj == "home" or obj == "":
            return 0.8
        else:
            return None  # defaults to 0.5 when unset
