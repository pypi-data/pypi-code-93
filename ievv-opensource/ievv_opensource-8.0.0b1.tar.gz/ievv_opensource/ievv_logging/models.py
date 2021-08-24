from django.contrib.postgres.fields import JSONField
from django.db import models


class IevvLoggingEventBase(models.Model):
    slug = models.CharField(max_length=255, unique=True, db_index=True)
    last_started = models.DateTimeField()
    last_finished = models.DateTimeField(null=True, blank=True)
    time_spent = models.CharField(max_length=255, null=False, blank=True, default='')
    time_spent_in_seconds = models.IntegerField(null=True, blank=True)
    success_run = models.BooleanField(null=True, default=None)

    def __str__(self):
        return self.slug

    class Meta:
        ordering = ['-id']


class IevvLoggingEventItem(models.Model):
    logging_base = models.ForeignKey(IevvLoggingEventBase, on_delete=models.CASCADE)
    time_spent = models.CharField(max_length=255, null=False, blank=True, default='')
    time_spent_in_seconds = models.IntegerField(null=True, blank=True)
    success_run = models.BooleanField(null=True, default=None)
    data = models.JSONField(null=True, blank=True)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(null=True, blank=True)
    created_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.logging_base}'

    class Meta:
        ordering = ['-id']
