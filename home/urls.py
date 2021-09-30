from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import RedirectView
from django.urls import path, include

from home import views
from home.models import AdjacencyModel

tp = AdjacencyModel.Type

sitemaps = {"static_pages": views.StaticViewSitemap}

urlpatterns = [
	path('', views.HomeView.as_view(), name = 'home'),
	path('activites/', views.ActivityView.as_view(), name = 'activites'),
	path('activites/nouvelle/', views.ActivitySubmissionView.as_view(), name = 'activity_submission'),
	path('faq/', views.FAQView.as_view(), name = 'FAQ'),
	path('table/<int:id>', views.TableView.as_view(), name = 'table'),
	path('table/<int:id>/new', views.TableView.as_view(style=tp.START), name = 'table_new'),
	path('table/<int:id>/join', views.TableView.as_view(style=tp.MIDDLE), name = 'table_join'),
	path('tables', views.TablesView.as_view(), name = 'tables'),
	path('favicon.ico', RedirectView.as_view(url='/static/imgs/favicon.ico')),
	path(
		'sitemap.xml', sitemap, {'sitemaps': sitemaps},
		name='django.contrib.sitemaps.views.sitemap'
	),
	path('admin_pages/', include(('admin_pages.urls', 'admin_pages'), namespace="admin_pages")),
	path("authens/logout", views.LogoutView.as_view(), name="logout"),
	path("authens/", include("authens.urls")),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
