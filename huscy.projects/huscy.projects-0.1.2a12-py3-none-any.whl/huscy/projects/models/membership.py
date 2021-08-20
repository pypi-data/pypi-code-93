from django.conf import settings
from django.db import models

from .project import Project


class Membership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    is_coordinator = models.BooleanField(default=False)

    def has_write_permission(self):
        return self.user.has_perm('change_project', self.project)

    def __str__(self):
        return f'{self.user.get_full_name()} is member in project {self.project.title}'

    class Meta:
        unique_together = 'user', 'project'
