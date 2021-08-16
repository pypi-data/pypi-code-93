from functools import wraps
from rest_framework.response import Response


def list_model(func):
    @wraps(func)
    def inner(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.service.list_model())
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    return inner
