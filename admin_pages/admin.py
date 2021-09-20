from django.contrib import admin
from django.contrib.auth.models import Group

# We don't use groups, let's hide them
admin.site.unregister(Group)
