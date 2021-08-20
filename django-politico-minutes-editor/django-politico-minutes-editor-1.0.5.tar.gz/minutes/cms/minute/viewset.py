from minutes.models import Minute, MinuteType, User
from django.utils.text import slugify
from .serializers import MinuteSerializer
from ..common.serializers import UserSerializer, MinuteTypeSerializer
from ..common.viewsets.base import BaseCMSViewset


class MinuteViewset(BaseCMSViewset):
    session_model = Minute
    queryset = Minute.objects.all()
    serializer_class = MinuteSerializer

    def context(self):
        return {
            "user": UserSerializer(User.objects.all(), many=True).data,
            "minute_type": MinuteTypeSerializer(
                MinuteType.objects.all(), many=True
            ).data,
        }

    def create(self, request):
        if (
            "slug" not in request.data
            or request.data["slug"] is None
            or request.data["slug"] == ""
        ):
            request.data["slug"] = slugify(request.data["handle"])
        return super().create(request)

    def update(self, request, pk=None):
        if (
            "slug" not in request.data
            or request.data["slug"] is None
            or request.data["slug"] == ""
        ):
            request.data["slug"] = slugify(request.data["handle"])
        return super().update(request, pk)
