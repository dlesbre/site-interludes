from site_settings.models import SiteSettings

def settings(request):
	return {'settings': SiteSettings.load()}
