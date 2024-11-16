from site_settings import constants
from site_settings.models import SiteSettings, SponsorModel, get_year


def settings(request):
    return {
        "settings": SiteSettings.load(),
        "constants": constants,
        "year": get_year(),
        "sponsors": SponsorModel.objects.filter(display=True).order_by("name"),
    }
