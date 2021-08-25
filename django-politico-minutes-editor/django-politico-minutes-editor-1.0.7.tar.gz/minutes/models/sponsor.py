import uuid
from django.db import models


class Sponsor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    logo = models.URLField(max_length=200)
    last_updated = models.DateTimeField(auto_now=True)
    sponsored_text = models.TextField(default="Sponsored by")

    def __str__(self):
        return self.name
