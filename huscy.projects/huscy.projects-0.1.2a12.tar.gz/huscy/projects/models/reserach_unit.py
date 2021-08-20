from uuid import uuid4

from django.conf import settings
from django.db import models


def get_default_value_for_code():
    return uuid4().hex


class ResearchUnit(models.Model):
    name = models.CharField(max_length=128, unique=True)
    code = models.CharField(max_length=32, unique=True, blank=True,
                            default=get_default_value_for_code)
    principal_investigator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.name} ({self.principal_investigator.get_full_name()})'
