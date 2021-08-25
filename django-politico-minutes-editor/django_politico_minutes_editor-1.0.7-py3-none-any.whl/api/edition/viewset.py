from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from minutes.models import Edition, Vertical

from minutes.api.common.serializers import (
    EditionSerializer,
    EditionLiveSerializer
)
from minutes.api.common.viewsets import BaseApiReadOnlyViewset


class EditionViewset(BaseApiReadOnlyViewset):
    queryset = Edition.objects.all()
    serializer_class = EditionSerializer

    def list(self, request):
        vertical_slug = request.GET.get("v", None)
        v = get_object_or_404(Vertical, slug=vertical_slug)

        return Response(
            self.serializer_class(Edition.objects.latest_live(v)).data
        )

    @action(detail=True, methods=["get"])
    def live(self, request, pk=None):
        edition = self.get_object()

        return Response(
            EditionLiveSerializer(edition).data
        )
