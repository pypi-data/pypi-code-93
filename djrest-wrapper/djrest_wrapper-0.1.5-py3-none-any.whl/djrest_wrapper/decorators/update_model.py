
from functools import wraps
from rest_framework.response import Response


def update_model(func):
    @wraps(func)
    def inner(self, request, pk, *args, **kwargs):
        reqser = self.get_serializer(data=request.data)
        reqser.is_valid(raise_exception=True)
        id = pk
        model = self.service.update_model_by_id(id, reqser.data)
        func(self, request, pk, *args, **kwargs)
        resser = self.get_serializer_response()(model)
        return Response(data={model.__class__.__name__.lower(): resser.data})
    return inner
