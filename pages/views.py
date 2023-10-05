from django.http import Http404
from django.views.generic import DetailView
from django.conf import settings
from django.template import Context, Template

from os.path import join

from site_settings.models import SiteSettings
from home.models import ActivityModel
from home.views import get_planning_context

from .models import HTMLPageModel

PREBUILT_PAGES = [
    {"name": "home", "slug": "", "file": "home.html"},
    {"name": "activites", "slug": "activites", "file": "activites.html"},
    {"name": "faq", "slug": "faq", "file": "faq.html"},
]

PREBUILT_PAGES_ROOT = join(settings.BASE_DIR, "pages/default")


# Create your views here.
class HTMLPageView(DetailView):
    """Affiche une page quelquonque depuis une URL dynamique"""

    template_name = "html_page.html"
    model = HTMLPageModel

    def get_context_data(self, **kwargs):
        """Adds the page data and slug to template render context"""
        context = super().get_context_data(**kwargs)
        context["slug"] = self.object.slug
        context["settings"] = SiteSettings.load()
        context["activities"] = ActivityModel.objects.filter(display=True).order_by(
            "title"
        )
        context.update(get_planning_context())
        template = Template(self.object.content)
        context["html_body"] = template.render(context=Context(context))
        return context

    def get_object(self, queryset=None):
        """Get the page from the slug,
        If no model exists, looks for default pages and saves them"""
        try:
            obj = super().get_object(queryset)
        except Http404 as err:
            slug = self.kwargs.get(self.slug_url_kwarg)
            for page in PREBUILT_PAGES:
                if page["slug"] == slug:
                    with open(join(PREBUILT_PAGES_ROOT, page["file"]), "r") as file:
                        content = file.read()
                    obj = HTMLPageModel(slug=slug, name=page["name"], content=content)
                    obj.save()
                    return obj
            raise err
        if not obj.visible:
            raise Http404()
        return obj
