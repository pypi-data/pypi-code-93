from sqlalchemy import inspect, Column
from sqlalchemy.ext.hybrid import HYBRID_PROPERTY
from sqlalchemy.ext.associationproxy import ASSOCIATION_PROXY


class InspectionMixin:
    __abstract__ = True
    __cytra_inspections__: dict = None

    @classmethod
    def _update_inspections(cls):
        # inspected attributes tuple: (type_, key, info, col)
        res = dict(
            all=[],
            all_by_key={},
            hybrid_properties=[],
            relationships=[],
            composites=[],
            synonyms=[],
            columns=[],
            proxies=[],
        )
        mapper = inspect(cls)
        for k, c in mapper.all_orm_descriptors.items():

            if k == "__mapper__":  # pragma:nocover
                continue

            if c.extension_type == ASSOCIATION_PROXY:
                cc_type = "proxies"

            elif c.extension_type == HYBRID_PROPERTY:
                cc_type = "hybrid_properties"

            elif k in mapper.relationships:
                cc_type = "relationships"

            elif k in mapper.synonyms:
                cc_type = "synonyms"

            elif k in mapper.composites:
                cc_type = "composites"

            else:
                cc_type = "columns"

            ic = (
                cc_type,
                cls.get_column_key(c),
                cls.get_column_info(c),
                getattr(cls, k),
            )
            res[cc_type].append(ic)
            res["all"].append(ic)
            res["all_by_key"][ic[1]] = ic
        return res

    @classmethod
    def get_inspections(cls):
        if cls.__cytra_inspections__ is None:
            cls.__cytra_inspections__ = cls._update_inspections()

        return cls.__cytra_inspections__

    @classmethod
    def get_column_info(cls, column: Column) -> dict:
        # Use original property for proxies
        if hasattr(column, "original_property") and column.original_property:
            info = column.info.copy()
            info.update(column.original_property.info)
            return info

        return column.info

    @classmethod
    def get_column_key(cls, column: Column) -> str:
        if hasattr(column, "key"):
            return column.key

        # for `hybrid_property`
        return column.__name__
