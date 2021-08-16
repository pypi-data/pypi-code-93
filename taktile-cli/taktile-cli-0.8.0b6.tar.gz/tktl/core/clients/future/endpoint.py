import re
import typing as t

from pyarrow.flight import ActionType, FlightClient, Ticket  # type: ignore
from pydantic import BaseModel

from tktl.core.clients.future.http import API
from tktl.core.exceptions.exceptions import APISwitchException
from tktl.core.loggers import LOG
from tktl.core.schemas.future.service import EndpointInfoSchema
from tktl.core.serializers import deserialize_arrow

from .utils import batch_arrow, safe_post


class EndpointActionGroup(BaseModel):
    endpoint: ActionType
    X: ActionType
    y: ActionType


class SDKRestEndpoint:
    """SDKRestEndpoint.

    This is a SDK Rest endpoint, exposing function calling through
    `__call__` and explainer endpoints through `explain`.
    """

    def __init__(self, *, api: API, info: EndpointInfoSchema):
        self._api = api
        self._info = info
        self.__name__ = info.name
        self._y: t.Any = None

    def __call__(self, X: t.Any, retries: int = 3, timeout: float = 10.0) -> t.Any:
        try:
            return safe_post(
                api=self._api,
                url=self._info.path,
                json=X,
                retries=retries,
                timeout=timeout,
            )
        except APISwitchException as e:
            # TODO: Remove this in taktile-cli 1.0
            if self._info.path.startswith("/model"):
                LOG.warning("404, switching from classic to future")
                self._info.path = re.sub(r"^/model", "/endpoints", self._info.path)
            elif self._info.path.startswith("/endpoints"):
                LOG.warning("404, switching from future to classic")
                self._info.path = re.sub(r"^/endpoints", "/model", self._info.path)
            else:
                LOG.error("404 on unknown path")
                raise APISwitchException("404 on unknown path") from e

            return safe_post(
                api=self._api,
                url=self._info.path,
                json=X,
                retries=retries,
                timeout=timeout,
            )

    def explain(self, X: t.Any, retries: int = 3, timeout: float = 10.0) -> t.Any:
        if not self._info.explain_path:
            raise ValueError(
                "The endpoint {self._info.name} if so type {self._info.kind}"
                " and does not have an explain endpoint"
            )
        return safe_post(
            api=self._api,
            url=self._info.explain_path,
            json=X,
            retries=retries,
            timeout=timeout,
        )

    def X(self) -> t.Any:
        return self._info.input_example

    def y(self) -> t.Any:
        # Use functools.cache when upgrading to Python 3.8
        if not self._y:
            self._y = safe_post(
                api=self._api, url=self._info.path, json=self._info.input_example
            )
        return self._y


class SDKArrowEndpoint:
    """SDKArrowEndpoint.

    This is a SDK Arrow endpoint, exposing function calling through
    `__call__` and sample data through `X` and `y`.
    """

    def __init__(self, *, client: FlightClient, action_group: EndpointActionGroup):
        self._client = client
        self._action_group = action_group
        self.__name__ = action_group.endpoint.type

    def __call__(self, X: t.Any) -> t.Any:
        return batch_arrow(client=self._client, action=self._action_group.endpoint, X=X)

    def X(self) -> t.Any:
        reader = self._client.do_get(Ticket(ticket=self._action_group.X.type))
        return deserialize_arrow(reader.read_all())

    def y(self) -> t.Any:
        reader = self._client.do_get(Ticket(ticket=self._action_group.y.type))
        return deserialize_arrow(reader.read_all())


class RestEndpoints:
    """RestEndpoints.

    This is the `endpoints` object on TaktileSDK Rest Clients.
    """

    def __init__(self, *, api: API, infos: t.List[EndpointInfoSchema]):

        for info in infos:
            setattr(self, info.name, SDKRestEndpoint(api=api, info=info))


class ArrowEndpoints:
    """ArrowEndpoints.

    This is the `endpoints` object on TaktileSDK Arrow Clients.
    """

    def __init__(self, *, client: FlightClient, actions: t.List[ActionType]):

        action_types = [a.type for a in actions]
        action_groups = []

        for action in actions:

            if (
                action.type + "__X" in action_types
                and action.type + "__y" in action_types
            ):
                action_groups.append(
                    EndpointActionGroup(
                        endpoint=action,
                        X=[a for a in actions if a.type == action.type + "__X"][0],
                        y=[a for a in actions if a.type == action.type + "__y"][0],
                    )
                )

        for group in action_groups:
            setattr(
                self,
                group.endpoint.type,
                SDKArrowEndpoint(client=client, action_group=group),
            )
