import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models

from concurrency.fields import AutoIncVersionField


class Minute(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    handle = models.CharField(max_length=100)
    slug = models.SlugField(max_length=50)

    type = models.ForeignKey(
        "MinuteType", on_delete=models.PROTECT, related_name="+"
    )

    edition = models.ForeignKey(
        "Edition",
        on_delete=models.CASCADE,
        related_name="minutes",
        related_query_name="minutes",
    )

    author = models.ForeignKey(
        "User",
        on_delete=models.PROTECT,
        related_name="minutes",
        related_query_name="minutes",
    )

    last_updated = models.DateTimeField(auto_now=True)

    last_published = models.DateTimeField(blank=True, null=True)

    ready_to_publish = models.BooleanField(default=False)

    version = AutoIncVersionField()

    content = JSONField(blank=True, null=True)

    edition_sort = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True
    )

    def __str__(self):
        return "{} – {}: {}".format(
            self.edition, self.edition_sort, self.handle
        )

    def production_link(self):
        edition_root = self.edition.production_link()
        self_root = self.slug + "/"
        return "{}{}".format(edition_root, self_root)
