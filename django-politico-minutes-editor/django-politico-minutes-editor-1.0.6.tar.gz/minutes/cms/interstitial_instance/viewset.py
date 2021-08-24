from rest_framework.response import Response
from minutes.utils.serialize_and_save import serialize_and_save
from minutes.models import InterstitialInstance
from .serializers import InterstitialInstanceSerializer
from ..common.serializers import InterstitialTypeSerializer
from ..common.viewsets.base import BaseCMSViewset


class InterstitialInstanceViewset(BaseCMSViewset):
    session_model = InterstitialInstance
    queryset = InterstitialInstance.objects.all()
    serializer_class = InterstitialInstanceSerializer

    def create(self, request):
        data = request.data.copy()
        serializer = self.serializer_class(data=data)
        serialize_and_save(serializer)

        return Response(serializer.data)

    def update(self, request, pk=None):
        data = request.data.copy()

        instance = self.queryset.get(id=pk)
        serializer = self.serializer_class(instance, data=data)
        serialize_and_save(serializer)

        return Response(serializer.data)
