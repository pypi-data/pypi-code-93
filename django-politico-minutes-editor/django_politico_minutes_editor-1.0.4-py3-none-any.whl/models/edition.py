import uuid
import pytz
from django.db import models
from django.utils import timezone
from django.conf import settings


new_york_tz = pytz.timezone("America/New_York")


class EditionManager(models.Manager):
    def latest_live(self, vertical):
        return (
            super()
            .get_queryset()
            .filter(
                live=True,
                publish_datetime__lte=timezone.now(),
                vertical=vertical,
            )
            .order_by("-publish_datetime")
            .first()
        )


class Edition(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    theme = models.ForeignKey(
        "Theme", on_delete=models.PROTECT, related_name="+"
    )

    vertical = models.ForeignKey(
        "Vertical",
        on_delete=models.PROTECT,
        related_name="editions",
        related_query_name="editions",
    )

    last_updated = models.DateTimeField(auto_now=True)

    live = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    publish_datetime = models.DateTimeField(unique=True)

    sponsor = models.ForeignKey(
        "Sponsor",
        on_delete=models.PROTECT,
        related_name="+",
        null=True,
        blank=True,
    )

    objects = EditionManager()

    def __str__(self):
        return self.publish_datetime.astimezone(new_york_tz).strftime(
            "%b %d, %Y – %-I:%M %p"
        )

    def should_publish(self):
        return (
            not self.is_published
            and self.live
            and self.publish_datetime <= timezone.now()
        )

    def is_latest_live(self):
        return Edition.objects.latest_live(self.vertical) == self

    def published_datetime_slug(self):
        return self.publish_datetime.astimezone(new_york_tz).strftime(
            "%m-%d-%Y"
        )

    def preview_link(self):
        domain_root = (
            "http://staging.interactives.politico.com.s3.amazonaws.com"
        )
        minutes_root = settings.MINUTES_PUBLISH_ROOT
        vertical_root = "/" + self.vertical.slug
        return "{}{}{}/preview/{}/index.html".format(
            domain_root, minutes_root, vertical_root, self.id
        )

    def production_link(self):
        domain_root = "https://politico.com"
        minutes_root = settings.MINUTES_PUBLISH_ROOT
        vertical_root = "/" + self.vertical.slug
        edition_root = "/" + self.published_datetime_slug() + "/"
        return "{}{}{}{}".format(
            domain_root, minutes_root, vertical_root, edition_root
        )

    class Meta:
        ordering = ["-publish_datetime"]
