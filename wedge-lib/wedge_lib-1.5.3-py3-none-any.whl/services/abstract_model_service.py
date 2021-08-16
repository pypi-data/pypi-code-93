from django.db import models
from typing import List
from w.services.abstract_service import AbstractService
from w import exceptions


# noinspection PyCallingNonCallable
from w.services.technical.dict_service import DictService


class AbstractModelService(AbstractService):
    _model: models.Model

    @staticmethod
    def _is_field(field):
        """Check if field from model._meta.get_fields() is field"""
        return hasattr(field, "related_name") is False

    @classmethod
    def list_fields(cls) -> list:
        """List model fields"""
        return [f.name for f in cls._model._meta.get_fields() if cls._is_field(f)]

    @classmethod
    def clean_attrs(cls, attrs):
        """Remove unexpected model attributes"""
        return DictService.keep_keys(attrs, cls.list_fields())

    @classmethod
    def create(cls, **attrs):
        """
        Create model instance

        Args:
            **attrs: model attributes values

        Returns:
            models.Model
        """
        instance = cls._model(**attrs)
        instance.save()
        return instance

    @classmethod
    def get_by_pk(cls, pk):
        """
        Retrieve model by its primary key

        Returns:
            Model
        """
        return cls._model.objects.get(pk=pk)

    @classmethod
    def get_if_exists(cls, **filters):
        """Retrieve instance if exists else return None"""
        qs = cls._model.objects.filter(**filters)
        if qs.exists():
            return qs.first()
        return None

    @classmethod
    def is_exists_by_pk(cls, pk) -> bool:
        """
        Check model existsby its primary key

        Returns
            bool
        """
        qs = cls._model.objects.filter(pk=pk)
        return qs.exists()

    @classmethod
    def check_by_pk(cls, pk):
        """
        Check model exists by its primary key

        if found return model else raise NotFoundError

        Raises
            NotFoundError
        """
        try:
            return cls._model.objects.get(pk=pk)
        except cls._model.DoesNotExist:
            label = cls._model._meta.verbose_name.title()  # noqa
            raise exceptions.NotFoundError(f"{label} not found (pk={pk})")

    @classmethod
    def list(cls, **filters) -> models.QuerySet:
        """
        List models filtered by filters (optional)

        Args:
            **filters: filter result

        Returns:
            QuerySet
        """
        if filters:
            return cls._model.objects.filter(**filters)
        return cls._model.objects.all()

    @classmethod
    def list_pks(cls, **filters) -> List:
        """
        List model pks filtered by filters (optional)

        Args:
            **filters:

        Returns:
            List
        """
        return cls.list(**filters).values_list("pk", flat=True)

    @classmethod
    def update(cls, instance, **attrs):
        """
        Update model instance

        Args:
            instance: model instance to update
            **attrs: model attributes values

        Returns:
            models.Model
        """
        update_it = False
        for attr, value in attrs.items():
            if getattr(instance, attr) != value:
                setattr(instance, attr, value)
                update_it = True

        if update_it:
            instance.save()
        return instance

    @classmethod
    def delete(cls, filters) -> int:
        """
        Delete

        Args:
            filters: model filters to delete

        Returns:
            nb deleted
        """
        nb, _ = cls._model.objects.filter(**filters).delete()
        return nb

    @classmethod
    def delete_by_pk(cls, pk) -> int:
        """
        Delete a model by is primary key

        Args:
            pk: model pk to delete

        Returns:
            nb deleted
        """
        return cls.delete({"pk": pk})

    @classmethod
    def to_dict(cls, instance):
        return {f: getattr(instance, f) for f in cls.list_fields()}
