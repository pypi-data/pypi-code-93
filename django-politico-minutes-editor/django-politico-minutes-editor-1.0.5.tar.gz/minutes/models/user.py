import uuid

from django.db import models
from django.conf import settings

REPORTER = "REP"
ADVERTISER = "ADV"
ADMIN = "ADM"


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=3,
        default=REPORTER,
        choices=[
            (REPORTER, "Reporter"),
            (ADVERTISER, "Advertiser"),
            (ADMIN, "Admin"),
        ],
    )
    bio_link = models.URLField(max_length=200, blank=True, null=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )

    @staticmethod
    def get_from_user(user):
        try:
            return User.objects.get(user=user)
        except User.DoesNotExist:
            return None

    def __str__(self):
        return str(self.user)
