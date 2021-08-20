from minutes.utils.api_auth import ReadOnlyTokenAuthedViewSet
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class BaseApiReadOnlyViewset(ReadOnlyTokenAuthedViewSet):
    pagination_class = None
    throttle_classes = []
