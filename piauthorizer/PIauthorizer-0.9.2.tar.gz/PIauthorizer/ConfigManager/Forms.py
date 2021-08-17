from typing import Dict, Optional

from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from pydantic.main import BaseModel
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED


class OAuthFlow(BaseModel):
    refreshUrl: Optional[str] = None
    scopes: Dict[str, str] = {}


class OAuthFlowImplicit(OAuthFlow):
    authorizationUrl: str


class OAuthFlowAuthorizationCode(OAuthFlow):
    authorizationUrl: str
    tokenUrl: str


class OAuthFlowsModel(BaseModel):
    implicit: Optional[OAuthFlowImplicit] = None
    authorizationCode: Optional[OAuthFlowAuthorizationCode] = None


class OAuth2ImplicitCodeBearer(OAuth2):
    def __init__(
        self,
        authorizationUrl: str,
        tokenUrl: str,
        refreshUrl: Optional[str] = None,
        scheme_name: Optional[str] = None,
        scopes: Optional[Dict[str, str]] = {},
        auto_error: bool = True,
    ):
        flows = OAuthFlowsModel(
            implicit={
                "tokenUrl": tokenUrl,
                "authorizationUrl": authorizationUrl,
                "refreshUrl": refreshUrl,
                "scopes": scopes,
            }
        )
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        authorization: str = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


class Token(BaseModel):
    token: str
    tenant_name: str
    tenant_id: str
    tenant_config: dict = {}
