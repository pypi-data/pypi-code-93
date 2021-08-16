from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT
from ..decorators import serializer_validation

class CreateMixin(mixins.CreateModelMixin):
    @serializer_validation
    def create(self, request, *args, **kwargs):
        reqser = self.get_serializer(data=request.data)
        reqser.is_valid(raise_exception=True)
        model = self.perform_create(reqser)
        resser = self.get_serializer_response()(model)
        return Response(data={model.__class__.__name__.lower(): resser.data}, status=HTTP_201_CREATED)

    def perform_create(self, serializer):
        return serializer.save()


class UpdateMixin(mixins.UpdateModelMixin):
    @serializer_validation
    def update(self, request, pk, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        model = self.perform_update(serializer)
        resser = self.get_serializer_response()(model)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(data={model.__class__.__name__.lower(): resser.data})

    def perform_update(self, serializer):
        return serializer.save()


class RetrieveMixin(mixins.RetrieveModelMixin):
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        resser = self.get_serializer_response()(instance)
        return Response(data={instance.__class__.__name__.lower(): resser.data})


class DestroyMixin(mixins.DestroyModelMixin):
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(data={}, status=HTTP_204_NO_CONTENT)


class ListMixin(mixins.ListModelMixin):
    pass
