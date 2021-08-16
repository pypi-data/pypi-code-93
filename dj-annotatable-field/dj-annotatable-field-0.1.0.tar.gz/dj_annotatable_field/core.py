import functools
import typing

from django.db import models
from django.db.models import Manager
from django.db.models import QuerySet


class AnnotateFieldsMixin:
    model: models.Model
    annotate: typing.Callable

    def annotate_fields(self, *args, exclude=None):
        exclude = exclude or []
        include = args or [
            name
            for name, field in vars(self.model).items()
            if isinstance(field, AnnotatableField)
        ]
        kwargs = {}
        for name in set(include) - set(exclude):
            field = getattr(self.model, name)
            kwargs.update(field.annotation)
        return self.annotate(**kwargs)


class AnnotatableFieldsQuerySet(QuerySet, AnnotateFieldsMixin):
    pass


class AnnotatableFieldsManager(Manager.from_queryset(AnnotatableFieldsQuerySet)):
    pass


class AnnotatableField:
    def __init__(
        self,
        expr,
        *,
        source: typing.Union[str, typing.Callable] = None,
        default: typing.Any = None,
        annotation_name: typing.Optional[str] = None,
    ):
        self.expr = expr
        self.default = default
        self._source = source
        self._annotation_name = annotation_name
        super().__init__()

    def source(self, fn):
        assert self._source is None, (
            f"{self.__class__.__name__}.{self.name} must pass source as a string, callable or implement a "
            f"method decorated with @{self.name}.source"
        )

        self._source = fn

    @property
    def annotation(self) -> dict:
        return {self.annotation_name: self.expr}

    @property
    def annotation_name(self) -> str:
        if self._annotation_name is not None:
            return self._annotation_name
        return f"_{self.name}"

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype):
        sentinel = object()
        if obj is None:
            return self

        assert self._source is not None, (
            f"{obj.__class__.__name__}.{self.name} must pass source as a string, callable or implement a "
            f"method decorated with @{self.name}.source"
        )
        value = getattr(obj, self.annotation_name, sentinel)
        if value is not sentinel:
            return value

        if callable(self._source):
            value = self._source(obj)
        else:
            value = rgetattr(obj, self._source, sentinel)

            if value is sentinel:
                value = self.default

        return value


def rgetattr(obj, attr, *args):
    """
    recursive getattr split on "."

    >>> rgetattr(obj, "user.profile.username", "")

    """

    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return functools.reduce(_getattr, [obj] + attr.split("."))
