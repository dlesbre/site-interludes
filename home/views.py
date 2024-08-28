from datetime import timedelta

from authens.views import LogoutView as AuthensLogoutView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sitemaps import Sitemap
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView

from pages.models import HTMLPageModel
from site48h import settings as site_settings
from site_settings.models import SiteSettings

from .forms import ActivitySubmissionForm
from .models import SlotModel


def get_planning_context():
    """Returns the context dict needed to display the planning"""
    settings = SiteSettings.load()
    context = dict()
    context["planning"] = SlotModel.objects.filter(on_planning=True).order_by("title")
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
# Activity Submission Form
# ==============================


class ActivitySubmissionView(LoginRequiredMixin, FormView):
    """Vue pour proposer une activité"""

    template_name = "activity_submission.html"
    form_class = ActivitySubmissionForm
    success_url = reverse_lazy("pages:html_page", kwargs={"slug": "activites"})

    @staticmethod
    def submission_check():
        """Vérifie si le formulaire est ouvert ou non"""
        settings = SiteSettings.load()
        return settings.activity_submission_open

    def not_open(self, request):
        """Appelé quand le formulaire est désactivé"""
        messages.error(request, "La soumission d'activité est désactivée")
        return redirect(self.success_url, permanent=False)

    def get_initial(self):
        init = super().get_initial()
        user = self.request.user
        init.update({"host_name": user.username, "host_email": user.email})
        return init

    def get(self, request, *args, **kwargs):
        if not self.submission_check():
            return self.not_open(request)
        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not self.submission_check():
            return self.not_open(request)
        form = self.form_class(request.POST)
        if not form.is_valid():
            context = self.get_context_data()
            context["form"] = form
            return render(request, self.template_name, context)

        activity = form.save()

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


class StaticViewSitemap(Sitemap):
    """Vue générant la sitemap.xml du site"""

    changefreq = "monthly"

    def items(self):
        """list of pages to appear in sitemap"""
        return [
            ("pages:home", {}),
        ] + [("pages:html_page", {"slug": obj.slug}) for obj in HTMLPageModel.objects.all() if obj.slug]

    def location(self, item):
        """real url of an item"""
        name, kwargs = item
        return reverse(name, kwargs=kwargs)

    def priority(self, obj):
        """priority to appear in sitemap"""
        # Priorize home page over the rest in search results
        if obj == "home" or obj == "":
            return 0.8
        else:
            return None  # defaults to 0.5 when unset


class LogoutView(AuthensLogoutView):
    next_page = reverse_lazy("pages:home")
