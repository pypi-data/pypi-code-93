
from functools import wraps
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED


def create_model(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        reqser = self.get_serializer(data=request.data)
        reqser.is_valid(raise_exception=True)
        model = self.service.create_model(reqser.data)
        func(self, request, *args, **kwargs)
        resser = self.get_serializer_response()(model)
        return Response(data={model.__class__.__name__.lower(): resser.data}, status=HTTP_201_CREATED)
    return inner
