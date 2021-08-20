from django.contrib import admin

from huscy.projects import models


admin.site.register(models.Experiment)
admin.site.register(models.Project)
admin.site.register(models.ResearchUnit)
admin.site.register(models.Session)
