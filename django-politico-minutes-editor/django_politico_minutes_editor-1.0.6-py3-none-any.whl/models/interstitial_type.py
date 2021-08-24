import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models


class InterstitialType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    json_schema = JSONField(blank=True, null=True)
    ui_schema = JSONField(blank=True, null=True)
    context = JSONField(blank=True, null=True)

    def __str__(self):
        return self.name
