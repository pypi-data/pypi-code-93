from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import ValidationError

from ..core.signer import Signer


class APISignature(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        # get signature
        api_signature = request.headers.get('X-SignedRequest-Signature')
        if api_signature is None:
            return False
        # get context data
        company_id = request.query_params.get('rs_company_id', None)
        request.rs_company_id = int(company_id) if company_id else company_id
        user_id = request.query_params.get('rs_user_id', None)
        request.rs_user_id = int(user_id) if user_id else user_id
        if user_id:
            try:
                request.user = get_user_model().objects.get(pk=user_id)
            except get_user_model().DoesNotExist:
                raise ValidationError('Invalid user_id.')
        payload = f'{request.method}.{request.path}.{request.body.decode()}.{company_id}.{user_id}'
        # verify signature
        secret_key = settings.SIGNED_REQUEST_API_KEY
        signer = Signer(secret_key)
        return signer.verify(signature=api_signature, payload=payload.encode('utf-8'))
