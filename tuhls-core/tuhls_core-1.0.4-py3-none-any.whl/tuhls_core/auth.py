from typing import Any, Tuple

from django.conf import settings
from django.db.models.functions import Now
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key: str) -> Tuple[Any, Any]:
        token_user, token = super().authenticate_credentials(key)

        if settings.TOKEN_EXPIRE_SECONDS > 0:
            if (
                timezone.now() - token.created
            ).total_seconds() > settings.TOKEN_EXPIRE_SECONDS:
                token.delete()
                raise AuthenticationFailed("The Token is expired")
            token.created = Now()
            token.save()

        return token_user, token


class QueryStringBasedTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        key = request.GET.get("token", None)
        if key:
            return self.authenticate_credentials(key)
        return None
