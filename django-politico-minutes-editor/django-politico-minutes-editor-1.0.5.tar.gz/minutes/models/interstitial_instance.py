import uuid

from django.contrib.postgres.fields import JSONField
from django.db import models


class InterstitialInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edition_sort = models.PositiveSmallIntegerField(
        default=0, blank=True, null=True
    )

    interstitial = models.ForeignKey(
        "Interstitial",
        on_delete=models.CASCADE,
        related_name="editions",
        related_query_name="editions",
    )

    edition = models.ForeignKey(
        "Edition",
        on_delete=models.CASCADE,
        related_name="interstitials",
        related_query_name="interstitials",
    )

    def __str__(self):
        return "{} – {}: {}".format(
            self.edition, self.edition_sort, self.interstitial
        )
