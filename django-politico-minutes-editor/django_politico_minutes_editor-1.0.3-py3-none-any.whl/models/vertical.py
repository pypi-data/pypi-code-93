import uuid

from django.db import models


class Vertical(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=50, unique=True, null=True, blank=True)
    intro = models.TextField(null=True, blank=True)

    horizontal_logo = models.URLField(
        max_length=200, unique=True, null=True, blank=True
    )
    vertical_logo = models.URLField(
        max_length=200, unique=True, null=True, blank=True
    )
    centered_logo = models.URLField(
        max_length=200, unique=True, null=True, blank=True
    )

    def __str__(self):
        return self.name
