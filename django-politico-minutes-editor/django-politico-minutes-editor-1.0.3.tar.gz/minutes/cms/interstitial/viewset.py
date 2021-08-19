from rest_framework.response import Response
from rest_framework.decorators import action
from minutes.models import Interstitial, InterstitialType
from .serializers import InterstitialSerializer, InterstitialListSerializer
from ..common.serializers import InterstitialTypeSerializer
from ..common.viewsets.base import BaseCMSViewset


class InterstitialViewset(BaseCMSViewset):
    session_model = Interstitial
    queryset = Interstitial.objects.all()
    serializer_class = InterstitialSerializer

    def context(self):
        return {
            "interstitial_type": InterstitialTypeSerializer(
                InterstitialType.objects.all(), many=True
            ).data
        }

    @action(detail=False, methods=["get"])
    def list_all(self, request):
        serializer = InterstitialListSerializer(
            Interstitial.objects.all(), many=True
        )

        return Response(serializer.data)
