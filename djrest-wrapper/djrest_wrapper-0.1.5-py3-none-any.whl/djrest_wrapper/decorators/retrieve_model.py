
from functools import wraps
from rest_framework.response import Response


def retrieve_model(func):
    @wraps(func)
    def inner(self, request, pk, *args, **kwargs):
        id = pk
        model = self.service.retrieve_model_by_id(id)
        func(self, request, pk, *args, **kwargs)
        resser = self.get_serializer_response()(model)
        return Response(data={model.__class__.__name__.lower(): resser.data})
    return inner
