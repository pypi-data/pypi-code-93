import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from concurrency.fields import AutoIncVersionField


class Interstitial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)

    type = models.ForeignKey(
        "InterstitialType", on_delete=models.PROTECT, related_name="+"
    )
    last_updated = models.DateTimeField(auto_now=True)

    favorite = models.BooleanField(default=False)

    content = JSONField(blank=True, null=True)

    version = AutoIncVersionField()

    def __str__(self):
        return self.name
