from django.contrib import admin

from home.models import InterludesActivity, InterludesParticipant, ActivityList

admin.site.register(InterludesActivity)
admin.site.register(InterludesParticipant)
admin.site.register(ActivityList)
