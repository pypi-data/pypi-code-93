from itertools import count, filterfalse

from django.conf import settings
from django.db import models

from .reserach_unit import ResearchUnit


class ProjectManager(models.Manager):
    def get_next_local_id(self, research_unit):
        taken_values = self.filter(research_unit=research_unit).values_list('local_id', flat=True)
        return next(filterfalse(lambda x: x in set(taken_values), count(1)))


class Project(models.Model):
    research_unit = models.ForeignKey(ResearchUnit, on_delete=models.DO_NOTHING)
    local_id = models.PositiveIntegerField()

    title = models.CharField(max_length=126)

    description = models.TextField(blank=True, default='')

    principal_investigator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    objects = ProjectManager()

    @property
    def local_id_name(self):
        return f'{self.research_unit.code}-{self.local_id}'

    class Meta:
        ordering = '-id',
        unique_together = ('local_id', 'research_unit')
