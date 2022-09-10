from django.contrib import admin

from .models import HTMLPageModel

@admin.register(HTMLPageModel)
class HTMLPageModelAdmin(admin.ModelAdmin):
	list_display = ["name", "path", "visible"]
