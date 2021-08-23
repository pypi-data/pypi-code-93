__all__ = ['version']

import functools
from typing import Type, Generic, TypeVar, Dict, Any, Optional, List

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_dataclasses.field_utils import TypeInfo
from rest_framework_dataclasses.serializers import DataclassSerializer, SerializerFieldDefinition

from django_dataclass_autoserialize.__version__ import version

T = TypeVar('T')


class TGSerializer(DataclassSerializer[T], Generic[T]):

    def build_dataclass_field(self, field_name: str, type_info: TypeInfo) -> SerializerFieldDefinition:
        if hasattr(type_info.base_type, 'serializer') and callable(type_info.base_type.serializer):
            field_class = type_info.base_type.serializer()
            field_kwargs = {'many': type_info.is_many}
            return field_class, field_kwargs
        else:
            return super().build_dataclass_field(field_name=field_name, type_info=type_info)

    def parse_request(cls, request: Request) -> T:
        raise NotImplementedError()


class AutoSerialize:

    def to_response(self) -> Response:
        return Response(self.to_data())

    def to_data(self) -> Dict[str, Any]:
        return self.__class__.serializer()(self).data

    @classmethod
    def validate_data(cls: Type[T], data: T) -> T:
        """

        Args:
            data ():

        Returns:
            data if valid
        Raises:
            ValidationError if not
        """
        return data

    @classmethod
    def fields(cls) -> List[str]:
        """Field to include. If you wish to include a method(no arg) just put it after __all__"""
        return ['__all__']

    @classmethod
    def from_data(cls: Type[T], data: Dict[str, Any]) -> T:
        obj = cls.serializer()(data=data)
        obj.is_valid(raise_exception=True)
        return obj.save()

    @classmethod
    def from_get_request(cls: Type[T], request: Request) -> T:
        """ Convert from get_request

        Args:
            request ():

        Returns:

        """
        return cls.from_data(request.query_params.dict())  # List/Repeated isn't supported

    @classmethod
    def from_post_request(cls: Type[T], request: Request) -> T:
        return cls.from_data(request.data)

    @classmethod
    @functools.lru_cache
    def serializer(cls: Type[T]) -> Type[TGSerializer[T]]:

        class Serializer(TGSerializer[cls]):

            class Meta:
                dataclass = cls
                ref_name = cls.__name__  # for swagger
                fields = cls.fields()

            def validate(self, data) -> T:
                return cls.validate_data(data)

            @classmethod
            def parse_request(cls, request: Request) -> T:
                ser = cls(data=request.data)
                ser.is_valid(raise_exception=True)
                return ser.save()

        if hasattr(cls, 'example') and callable(cls.example):
            return swagger_add_example(cls.example())(Serializer)
        else:
            return Serializer


def swagger_post_schema(body_type: Optional[Type[AutoSerialize]],
                        response_types: Optional[Dict[int, Type[AutoSerialize]]] = None, **kwds):
    from drf_yasg.utils import swagger_auto_schema
    responses = build_swagger_response(response_types, kwds)
    return swagger_auto_schema(
        request_body=body_type.serializer() if body_type is not None else None,
        responses=responses,
        **kwds
    )


def swagger_get_schema(query_type: Optional[Type[AutoSerialize]],
                       response_types: Optional[Dict[int, Type[AutoSerialize]]] = None, **kwds):
    from drf_yasg.utils import swagger_auto_schema
    responses = build_swagger_response(response_types, kwds)
    return swagger_auto_schema(
        query_serializer=query_type.serializer() if query_type is not None else None,
        responses=responses,
        **kwds
    )


def build_swagger_response(response_types: Optional[Dict[int, Type[AutoSerialize]]],
                           kwds: Dict[str, Any]) -> Optional[Dict[int, DataclassSerializer]]:
    _responses: Dict[int, DataclassSerializer] = {}
    if 'response_type' in kwds:
        _responses.update(kwds)
        del kwds['response_type']
    if response_types is not None:
        _responses.update({k: v.serializer() for k, v in response_types.items()})
    responses = _responses if len(_responses) > 0 else None
    return responses


def swagger_add_example(example):
    """Decorate Serializer with this to add example to openapi doc

    Args:
        example (object): example object
    """

    def decorator(cls):
        if not hasattr(cls.Meta, 'swagger_schema_fields'):
            cls.Meta.swagger_schema_fields = {}
        cls.Meta.swagger_schema_fields["example"] = cls(example).data
        return cls

    return decorator
