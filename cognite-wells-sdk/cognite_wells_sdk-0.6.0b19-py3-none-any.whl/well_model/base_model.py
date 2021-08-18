from typing import Any, Dict, List

from pandas import DataFrame
from pydantic import BaseModel

from cognite.well_model.client.utils._auxiliary import to_camel_case

EXPANDABLE = ["WellDatum", "Wellhead", "DoubleWithUnit"]
DEFAULT_EXPAND = ("metadata", "datum", "wellhead", "datum_elevation", "water_depth")
DEFAULT_IGNORE = ("rows",)


class WellsBaseModel(BaseModel):
    """
    The datamodel-code-generator program solves snake_case a bit opposite of
    what we want. We want to use `asset_id` in code, and `assetId` in json.
    Since it uses snake_case in the model and camelCase in the alias, we have to
    generate dict() and json() by alias, so that the output is true to the
    openapi spec.
    """

    def dict(self, by_alias=True, **kwargs):
        return super().dict(by_alias=by_alias, **kwargs)

    def json(self, by_alias=True, **kwargs):
        return super().json(by_alias=by_alias, **kwargs)

    def dump(
        self, expand: List[str] = DEFAULT_EXPAND, ignore: List[str] = DEFAULT_IGNORE, camel_case: bool = False
    ) -> Dict[str, Any]:
        """Dump the instance into a json serializable Python data type.

        Args:
            expand (List[str]): classes to be expanded so their attributes are at the base level
            ignore (List[str]): attributes that should not be added to the dataframe
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """
        change_key = to_camel_case if camel_case else lambda x: x
        dumped = {
            change_key(key): value
            for key, value in self.__dict__.items()
            if value is not None and not key.startswith("_")
        }
        expand = [change_key(e) for e in expand]
        ignore = [change_key(i) for i in ignore]
        for element in ignore:
            if element in dumped.keys():
                del dumped[element]
        for key in expand:
            if key in dumped:
                if isinstance(dumped[key], dict):
                    dumped.update(dumped.pop(key))
                # Recursively dump objects we deem expandable
                elif type(dumped[key]).__name__ in EXPANDABLE:
                    datum_keys = dumped.pop(key).dump(camel_case=camel_case)
                    dumped.update({change_key(f"{key}_{k}"): v for k, v in datum_keys.items()})
                else:
                    raise AssertionError("Could not expand attribute '{}'".format(key))
        # the surveys have metadata stored as `string: Metadata`, so extract the value from the metadata if we have them
        for k, v in dumped.items():
            typ = type(v)
            if typ.__name__ == "Metadata" and typ.__class__.__module__ == "pydantic.main":
                dumped[k] = v.__root__
        return dumped

    def to_pandas(
        self,
        expand: List[str] = DEFAULT_EXPAND,
        ignore: List[str] = DEFAULT_IGNORE,
        camel_case: bool = True,
    ) -> DataFrame:
        ignore = [] if ignore is None else ignore
        dumped = self.dump(expand, ignore, camel_case=camel_case)
        df = DataFrame(columns=["value"])
        for name, value in dumped.items():
            df.loc[name] = [value]
        return df

    # override this method so that the default for jupyter is dataframe
    def _repr_html_(self):
        return self.to_pandas(camel_case=False)._repr_html_()
