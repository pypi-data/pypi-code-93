import json
from typing import Text, Optional, Dict, Any

import aiohttp
import logging
from sanic.exceptions import abort
import jwt

from convo.core import constants
from convo.core.channels.channel import InputSocket
from convo.core.channels.rest import RestApiInput
from convo.core.constants import BY_DEFAULT_REQUEST_TIMEOUT
from sanic.request import Request

log = logging.getLogger(__name__)

CONVERSATION_ID_HASH = "conversation_id"
JWT_USERNAME_HASH = "username"
INTERACTIVE_LEARNING_AUTHORIZATION = "clientEvents:create"


class ChatInput(RestApiInput):
    """Chat input channel for Convo X"""

    @classmethod
    def name(cls) -> Text:
        return "convo"

    @classmethod
    def from_cred(cls, credentials: Optional[Dict[Text, Any]]) -> InputSocket:
        if not credentials:
            cls.raise_missing_credentials_exception()

        return cls(credentials.get("url"))  # pytype: disable=attribute-error

    def __init__(self, url: Optional[Text]) -> None:
        self.base_url = url
        self.jwt_key = None
        self.jwt_algorithm = None

    async def _fetch_pub_key(self) -> None:
        pub_key_url = f"{self.base_url}/version"
        async with aiohttp.ClientSession() as session:
            async with session.get(
                pub_key_url, timeout=BY_DEFAULT_REQUEST_TIMEOUT
            ) as resp:
                response_status_code = resp.status
                if response_status_code != 200:
                    log.error(
                        "Failed to fetch JWT public key from URL '{}' with "
                        "status code {}: {}"
                        "".format(pub_key_url, response_status_code, await resp.text())
                    )
                    return
                rjs = await resp.json()
                pub_key_field = "keys"
                if pub_key_field in rjs:
                    self.jwt_key = rjs["keys"][0]["key"]
                    self.jwt_algorithm = rjs["keys"][0]["alg"]
                    log.debug(
                        "Fetched JWT public key from URL '{}' for algorithm '{}':\n{}"
                        "".format(pub_key_url, self.jwt_algorithm, self.jwt_key)
                    )
                else:
                    log.error(
                        "Retrieved json response from URL '{}' but could not find "
                        "'{}' field containing the JWT public key. Please make sure "
                        "you use an up-to-date version of Convo X (>= 0.20.2). "
                        "Response was: {}"
                        "".format(pub_key_url, pub_key_field, json.dumps(rjs))
                    )

    def _decode_jwt_hash(self, bearer_token: Text) -> Dict:
        authorize_head_value = bearer_token.replace(
            constants.BEARER_TOKEN_AFFIXES, ""
        )
        return jwt.decode(
            authorize_head_value, self.jwt_key, algorithms=self.jwt_algorithm
        )

    async def _decode_bearer_hash(self, bearer_token: Text) -> Optional[Dict]:
        if self.jwt_key is None:
            await self._fetch_pub_key()

        # noinspection PyBroadException
        try:
            return self._decode_jwt_hash(bearer_token)
        except jwt.exceptions.InvalidSignatureError:
            log.error("JWT public key invalid, fetching new one.")
            await self._fetch_pub_key()
            return self._decode_jwt_hash(bearer_token)
        except Exception:
            log.exception("Failed to decode bearer token.")

    async def _extract_sender_detail(self, req: Request) -> Optional[Text]:
        """Fetch user from the Convo X Admin API."""

        jwt_pay_load = None
        if req.headers.get("Authorization"):
            jwt_pay_load = await self._decode_bearer_hash(req.headers["Authorization"])

        if not jwt_pay_load:
            jwt_pay_load = await self._decode_bearer_hash(req.args.get("token"))

        if not jwt_pay_load:
            abort(401)

        if CONVERSATION_ID_HASH in req.json:
            if self._is_user_authorize_to_send_messages_to_conversation(
                jwt_pay_load, req.json
            ):
                return req.json[CONVERSATION_ID_HASH]
            else:
                log.error(
                    "User '{}' does not have permissions to send messages to "
                    "conversation '{}'.".format(
                        jwt_pay_load[JWT_USERNAME_HASH], req.json[CONVERSATION_ID_HASH]
                    )
                )
                abort(401)

        return jwt_pay_load[JWT_USERNAME_HASH]

    @staticmethod
    def _is_user_authorize_to_send_messages_to_conversation(
        jwt_payload: Dict, message: Dict
    ) -> bool:
        usr_scopes = jwt_payload.get("scopes", [])
        return INTERACTIVE_LEARNING_AUTHORIZATION in usr_scopes or message[
            CONVERSATION_ID_HASH
        ] == jwt_payload.get(JWT_USERNAME_HASH)
