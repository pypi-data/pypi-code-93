from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from . import signals
from .serializers import NotifySerializer


@method_decorator(csrf_exempt, name='dispatch')
class NotifyView(APIView):

    def post(self, request, format=None):
        serializer = NotifySerializer(data=request.data)
        if serializer.is_valid():
            self._emit_signal(
                serializer.data['name'], serializer.data
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _emit_signal(name, data):
        signals.notification_received.send(
            sender=None,
            name=name, data=data
        )
