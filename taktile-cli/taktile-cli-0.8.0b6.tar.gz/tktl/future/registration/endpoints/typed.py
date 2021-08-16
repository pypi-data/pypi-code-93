import typing as t

from pydantic import BaseModel

from tktl.core.future.t import EndpointKinds

from .abc import XType, YType
from .advanced import AdvancedEndpoint


class TypedEndpoint(AdvancedEndpoint):
    kind: EndpointKinds = EndpointKinds.TYPED

    @staticmethod
    def supported(
        *, X: XType = None, y: YType = None, profile: t.Optional[str] = None,
    ) -> bool:
        return (
            profile is None
            and isinstance(X, (type(BaseModel), type(t.Any)))
            and isinstance(y, (type(BaseModel), type(t.Any)))
        )
