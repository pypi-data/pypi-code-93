import logging
from minutes.utils.api_auth import TokenAuthedViewSet
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from minutes.models import EditingSession, Minute, Interstitial
from minutes.cms.common.serializers import EditingSessionSerializer


class EditingSessionViewset(TokenAuthedViewSet):
    queryset = EditingSession.objects.all()
    pagination_class = None
    throttle_classes = []
    serializer_class = EditingSessionSerializer

    def handle_custom_action(
        self, request, method_name, error_status=status.HTTP_409_CONFLICT
    ):
        data = request.data
        session_id = data.get("id")
        session = self.get_object()

        method = getattr(session, method_name)
        success = method(session_id)

        if success[0]:
            return Response(success[1])
        else:
            return Response(success[1], status=error_status)

    @action(detail=True, methods=["post"])
    def request_new_session(self, request, *args, **kwargs):
        return self.handle_custom_action(request, "request_new_session")

    @action(detail=True, methods=["post"])
    def request_close_session(self, request, *args, **kwargs):
        return self.handle_custom_action(request, "close_session")

    @action(detail=True, methods=["post"])
    def ping(self, request, *args, **kwargs):
        return self.handle_custom_action(request, "ping")

    @action(detail=True, methods=["post"])
    def force_open(self, request, *args, **kwargs):
        return self.handle_custom_action(request, "open_session")
