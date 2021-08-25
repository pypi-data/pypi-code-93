import hashlib
import json
from datetime import datetime
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from wagtail.search import index


class LegacySystemMixin(models.Model):
    legacy_id_field = ""
    last_imported_at = models.DateTimeField(null=True, editable=False)

    class Meta:
        abstract = True

    @classmethod
    def find_by_legacy_id(cls, id):
        try:
            return cls.objects.all().get(**{cls.legacy_id_field: int(id)})
        except cls.DoesNotExist:
            return

    @property
    def is_legacy(self):
        return bool(getattr(self, self.legacy_id_field))

    def is_stale(self, source_last_updated: datetime):
        return bool(
            self.last_imported_at and self.last_imported_at < source_last_updated
        )

    @classmethod
    def extra_search_fields(cls):
        return [
            index.FilterField("last_imported_at"),
            index.FilterField(cls.legacy_id_field),
            index.SearchField(cls.legacy_id_field),
        ]


class DrupalLegacyMixin(LegacySystemMixin):
    legacy_id_field = "drupal_id"
    drupal_id = models.IntegerField(null=True, editable=False, unique=True)

    class Meta:
        abstract = True


class CISDataMixin(LegacySystemMixin):
    legacy_id_field = "cis_id"
    cis_id = models.IntegerField(editable=False, unique=True)

    class Meta:
        abstract = True


class APIHashMixin(models.Model):
    # A SHA-1 hash of the last known API representation
    api_hash = models.CharField(max_length=40, blank=True, editable=False)

    class Meta:
        abstract = True

    @staticmethod
    def get_hash(value: Any) -> str:
        """
        Returns a hash of the supplied JSON-serializable value, for comparisson with other hashes.
        """
        dict_str = json.dumps(value, cls=DjangoJSONEncoder, sort_keys=True)
        return hashlib.sha1(dict_str.encode()).hexdigest()
