import typing as t

from tktl.core.future.t import EndpointKinds

from .abc import Endpoint, XType, YType


class AdvancedEndpoint(Endpoint):
    kind: EndpointKinds = EndpointKinds.ADVANCED

    @staticmethod
    def supported(
        *, X: XType = None, y: YType = None, profile: t.Optional[str] = None,
    ) -> bool:
        return profile is None and X is None and y is None
