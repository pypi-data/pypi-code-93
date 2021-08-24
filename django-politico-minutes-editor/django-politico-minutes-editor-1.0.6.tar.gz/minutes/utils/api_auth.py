from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils.decorators import method_decorator
from rest_framework import authentication, exceptions
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class TokenAPIAuthentication(authentication.BaseAuthentication):
    """
    DRF custom authentication class for viewsets.
    Uses app's secret key to authenticate AJAX requests.
    """

    def authenticate(self, request):
        # Don't enforce if DEBUG
        if settings.DEBUG:
            return (AnonymousUser, None)
        try:
            # Token should be prefixed with string literal "Token" plus
            # whitespace, e.g., "Token <TOKEN>".
            token = request.META.get("HTTP_AUTHORIZATION").split()[1]
        except:
            raise exceptions.AuthenticationFailed(
                "No token or incorrect token format"
            )

        if token == settings.MINUTES_API_TOKEN:
            return (AnonymousUser, None)
        raise exceptions.AuthenticationFailed("Unauthorized")


class TokenAuthedViewSet(ModelViewSet):
    """
    ViewSet class that restricts views to our bots token.
    Also disables the default pagination.
    """

    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = (IsAuthenticated,)


class ReadOnlyTokenAuthedViewSet(ReadOnlyModelViewSet):
    """
    Read only ViewSet class that restricts views to our bots token.
    Also disables the default pagination.
    """

    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = (IsAuthenticated,)


class TokenAuthedAPIView(APIView):
    """
    APIView class that restricts views to our bots token.
    Also disables the default pagination.
    """

    authentication_classes = (TokenAPIAuthentication,)
    permission_classes = (IsAuthenticated,)
