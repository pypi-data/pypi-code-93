
from functools import wraps
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT


def delete_model(func):
    @wraps(func)
    def inner(self, request, pk, *args, **kwargs):
        id = pk
        self.service.delete_model_by_id(id)
        func(self, request,pk, *args, **kwargs)
        return Response(data={}, status=HTTP_204_NO_CONTENT)
    return inner
