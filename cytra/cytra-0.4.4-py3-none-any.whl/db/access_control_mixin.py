from typing import Any, Iterable

from sqlalchemy import Column
from cytra.db import InspectionMixin


class AccessControlMixin(InspectionMixin):
    """
    Controls access to properties

    Note: All mixins must respect to this mixin while intracting with
    outside of the model.
    """

    @classmethod
    def get_readables(cls, context: Any = None) -> Iterable[Column]:
        inspections = cls.get_inspections()
        for ic in inspections["all"]:
            if ic[0] == "proxies" or ic[2].get("protected"):
                continue
            yield ic

    @classmethod
    def get_writables(cls, context: Any = None) -> Iterable[Column]:
        inspections = cls.get_inspections()
        for ic in inspections["all"]:
            if ic[0] == "relationships" or ic[2].get("readonly"):
                continue

            yield ic
