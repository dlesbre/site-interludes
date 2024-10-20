from site_settings import constants
from site_settings.models import SiteSettings, get_year


def settings(request):
    return {
        "settings": SiteSettings.load(),
        "constants": constants,
        "year": get_year(),
    }
