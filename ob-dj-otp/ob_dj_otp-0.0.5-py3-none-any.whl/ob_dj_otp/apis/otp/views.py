import logging

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, permissions, viewsets

from ob_dj_otp.apis.otp.serializers import (
    OTPRequestCodeSerializer,
    OTPVerifyCodeSerializer,
)

logger = logging.getLogger(__name__)


@method_decorator(
    name="create",
    decorator=swagger_auto_schema(
        operation_summary="OTP Auth & Register",
        operation_description="""
        OTP Endpoint can be used for authentication or registration.

        *Auth*:

        - Request `POST /{version}/otp/` with `phone_number`
        The backend will send a verification code for the specified number if a matching user found.
        - Request `POST /{version}/otp/` with `phone_number` and `verification_code`
        The backend will validate the code and return access and refresh token

        """,
        tags=["OTP Auth",],
        responses={},
    ),
)
class OneTimePairingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get_serializer_class(self):
        if "verification_code" in self.request.data.keys():
            return OTPVerifyCodeSerializer
        return OTPRequestCodeSerializer
