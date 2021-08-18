import jwt

from assembly_payments.services.base import BaseService
from assembly_payments.types import TokenRequest, Token


class TokenService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/tokens"

    def create(self, **kwargs):
        data = TokenRequest(**kwargs)
        response = self._execute(TokenService.POST, self.endpoint, data=data.dict(), headers={}, url=self.auth_url)
        expires_at = jwt.decode(response.get('access_token'), algorithms=["RS256"], options={"verify_signature": False}).get("exp")
        return Token(**response, expires_at=expires_at)
