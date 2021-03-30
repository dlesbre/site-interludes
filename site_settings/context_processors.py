from site_settings import constants
from site_settings.models import SiteSettings

def settings(request):
	return {
		'settings': SiteSettings.load(),
		'constants' : constants,
	}
