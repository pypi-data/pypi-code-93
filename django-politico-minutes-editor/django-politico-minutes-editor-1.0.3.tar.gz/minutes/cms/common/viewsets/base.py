from minutes.utils.api_auth import (
    TokenAuthedViewSet,
    ReadOnlyTokenAuthedViewSet,
)
from minutes.utils.serialize_and_save import serialize_and_save
from minutes.models import EditingSession
from rest_framework.response import Response
from rest_framework.status import HTTP_412_PRECONDITION_FAILED
from django.shortcuts import get_object_or_404
from concurrency.exceptions import RecordModifiedError


class BaseCMSReadOnlyViewset(ReadOnlyTokenAuthedViewSet):
    pagination_class = None
    throttle_classes = []

    def context(self):
        return {}

    def list(self, request):
        resp_data = {}
        resp_data[self.basename] = None
        resp_data["context"] = self.context()
        return Response(resp_data)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(instance)

        resp_data = {}
        resp_data[self.basename] = serializer.data
        resp_data["context"] = self.context()
        return Response(resp_data)


class BaseCMSViewset(TokenAuthedViewSet):
    pagination_class = None
    throttle_classes = []

    def context(self):
        return {}

    def list(self, request):
        resp_data = {}
        resp_data[self.basename] = None
        resp_data["context"] = self.context()
        return Response(resp_data)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(instance)

        resp_data = {}
        resp_data[self.basename] = serializer.data
        resp_data["context"] = self.context()
        return Response(resp_data)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)

        try:
            instance = serialize_and_save(serializer)
        except RecordModifiedError:
            return Response(
                {"error": "Record has been modified"},
                status=HTTP_412_PRECONDITION_FAILED,
            )

        if hasattr(self, "session_model") and self.session_model:
            es_kwargs = {}
            es_kwargs[self.session_model.__name__.lower()] = instance
            es = EditingSession(**es_kwargs)
            es.save()

        return Response(serializer.data)

    def update(self, request, pk=None):
        instance = self.queryset.get(id=pk)
        serializer = self.serializer_class(instance, data=request.data)

        try:
            serialize_and_save(serializer)
        except RecordModifiedError:
            return Response(
                {"error": "Record has been modified"},
                status=HTTP_412_PRECONDITION_FAILED,
            )

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        instance = get_object_or_404(self.queryset, pk=pk)
        instance.delete()
        return Response("OK")
