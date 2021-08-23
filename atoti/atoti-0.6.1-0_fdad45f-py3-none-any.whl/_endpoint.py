from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Optional

from py4j.java_collections import JavaMap

from ._py4j_utils import to_python_dict
from .pyapi.http_request import HttpRequest
from .pyapi.user import User

if TYPE_CHECKING:
    from ._local_session import LocalSession

    CallbackEndpoint = Callable[[HttpRequest, User, LocalSession[Any]], str]


@dataclass
class EndpointHandler:
    callback: CallbackEndpoint
    session: LocalSession
    name: str = "Python.EndpointHandler"

    def handleRequest(  # pylint: disable=invalid-name, too-many-positional-parameters
        self,
        url: str,
        username: str,
        roles: str,
        path_parameter_values: JavaMap,  # type: ignore
        body: Optional[str] = None,
    ) -> str:
        path_parameters = {
            str(key): str(value)
            for key, value in to_python_dict(path_parameter_values).items()
        }
        parsed_body = None if body is None else json.loads(body)
        request = HttpRequest(url, path_parameters, parsed_body)
        user = User(username, roles[1 : len(roles) - 1].split(", "))

        response_body = self.callback(
            request,
            user,
            self.session,
        )

        return json.dumps(response_body)

    def toString(self) -> str:  # pylint: disable=invalid-name
        return self.name

    class Java:
        """Code needed for Py4J callbacks."""

        implements = ["io.atoti.pyapi.EndpointHandler"]
