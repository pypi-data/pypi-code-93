import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from concurrency.fields import AutoIncVersionField


class NativeAd(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    handle = models.CharField(max_length=100)

    sponsor = models.ForeignKey(
        "Sponsor",
        on_delete=models.PROTECT,
        related_name="ads",
        related_query_name="ads",
    )

    last_updated = models.DateTimeField(auto_now=True)

    version = AutoIncVersionField()

    lede = models.CharField(max_length=100)

    body = JSONField(blank=True, null=True)

    image = models.URLField(max_length=200, blank=True, null=True)

    campaign_title = models.CharField(max_length=100, blank=True, null=True)

    campaign_link = models.URLField(max_length=200, blank=True, null=True)

    pixels = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{}: {}".format(
            self.sponsor, self.handle
        )
