# flake8: noqa F405
from typing import Type

from django.db.models import Prefetch, QuerySet
from django.utils.translation import gettext as _
from serpy import *  # noqa

from w.services.technical.date_service import DateService


class DateField(Field):
    def to_value(self, value):
        if value:
            return DateService.to_mysql_date(value)


class DatetimeField(Field):
    def to_value(self, value):
        if value:
            return DateService.to_mysql_datetime(value)


class ManyToManyField(Field):
    def __init__(
        self,
        serializer,
        attr=None,
        call=False,
        label=None,
        required=True,
    ):
        super().__init__(attr, call, label, required)
        self.serializer = serializer

    def to_value(self, value):
        if value and value.exists():
            return self.serializer(value.all(), many=True).data
        return []


class PhoneNumberField(Field):
    def to_value(self, value):
        if value:
            return value.as_e164


class FileField(Field):
    def to_value(self, value):
        return value.name if value else None


class TranslateField(Field):
    def to_value(self, value):
        return _(value) if value else ""


class CloudinaryField(Field):
    def to_value(self, value):
        return value.url if value else None


class SerpySerializer(Serializer):
    """
    Data serializer built on Serpy.

    It adds query_string optimization and add custom Fields

    @see serpy documentation
    """

    @classmethod
    def get_optimized_queryset(cls, qs, prefix_related=None) -> QuerySet:
        """
        Get optimal QuerySet for serialization

        Args:
            qs (QuerySet): query set to complete
            prefix_related (str): prefix to add (for internal usage)

        Returns:
            QuerySet
        """

        if cls.select_related():
            qs = qs.select_related(*cls._get_select_related(prefix_related))
        if cls.prefetch_related():
            qs = qs.prefetch_related(*cls._get_prefetch_related(prefix_related))
        for prefix, serializer in cls.serializer_related().items():
            prefix = f"{prefix_related}__{prefix}" if prefix_related else prefix
            qs = serializer.get_optimized_queryset(qs, prefix)
        return qs

    @classmethod
    def select_related(cls) -> list:
        """
        list of related attribute to select
        Returns:
            list
        """
        return []

    @classmethod
    def prefetch_related(cls) -> list:
        """
        list of related of attribute to prefetch
        Returns:
            list
        """
        return []

    @classmethod
    def serializer_related(cls) -> dict:
        """
        List of related serializer
        Returns:
            dict: {"<attribute>": <serializer class>, ...}
        """
        return {}

    @classmethod
    def _get_select_related(cls, prefix=None) -> list:
        """
        get related select prefixed if needed
        Args:
            prefix (str): prefix to add

        Returns:
            list
        """
        if prefix is None:
            return cls.select_related()
        return [f"{prefix}__{r}" for r in cls.select_related()]

    @classmethod
    def _get_prefetch_related(cls, prefix=None):
        """
        get related prefetc prefixed if needed
        Args:
            prefix (str): prefix to add

        Returns:
            list
        """
        if prefix is None:
            return cls.prefetch_related()

        result = []
        for r in cls.prefetch_related():
            if not isinstance(r, Prefetch):
                r = f"{prefix}__{r}"
            else:
                r.prefetch_through = f"{prefix}__{r.prefetch_through}"
                r.prefetch_to = f"{prefix}__{r.prefetch_to}"
            result.append(r)
        return result
