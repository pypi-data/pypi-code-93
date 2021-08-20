from django.db import models

from .project import Project


class Experiment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='experiments')

    title = models.CharField(max_length=64)
    description = models.TextField(blank=True, default='')

    order = models.PositiveSmallIntegerField()
