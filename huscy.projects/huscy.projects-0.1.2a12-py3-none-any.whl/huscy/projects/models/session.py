from datetime import timedelta

from django.conf import settings
from django.db import models

from .experiment import Experiment


class Session(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=64)
    order = models.PositiveSmallIntegerField()

    setup_time = models.DurationField(default=timedelta())
    duration = models.DurationField()
    teardown_time = models.DurationField(default=timedelta())

    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    max_number_of_participants = models.PositiveIntegerField(default=1)
