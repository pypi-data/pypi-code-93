from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from minutes.models import Vertical, Theme
from .serializers import VerticalSerializer, VerticalListSerializer
from ..common.viewsets.base import BaseCMSReadOnlyViewset
from ..common.serializers import ThemeSerializer


class VerticalViewset(BaseCMSReadOnlyViewset):
    queryset = Vertical.objects.all()
    serializer_class = VerticalSerializer

    def context(self):
        return {"theme": ThemeSerializer(Theme.objects.all(), many=True).data}

    def retrieve(self, request, pk):
        instance = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(instance)

        resp_data = {}
        resp_data[self.basename] = self.serializer_class(
            self.queryset.get(pk=pk), page=request.GET.get("page", None)
        ).data
        resp_data["context"] = self.context()

        return Response(resp_data)

    def list(self, request):
        data = VerticalListSerializer(self.queryset, many=True).data
        return Response(data)
