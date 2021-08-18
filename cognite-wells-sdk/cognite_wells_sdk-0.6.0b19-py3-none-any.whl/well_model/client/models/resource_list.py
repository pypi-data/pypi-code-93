from typing import Any, Dict, List

from pandas import DataFrame

from cognite.well_model.models import (
    NDS,
    NPT,
    GetSequenceDTO,
    SequenceGetData,
    SequenceMeasurements,
    Trajectory,
    TrajectoryData,
    Well,
    Wellbore,
)


class WDLResourceList:
    _RESOURCE = None

    def __init__(self, resources: List[Any]):
        self.data = resources
        for resource in resources:
            if resource is None or not isinstance(resource, self._RESOURCE):  # type: ignore
                raise TypeError(
                    f"All resources for class '{self.__class__.__name__}' must be of type"  # type: ignore
                    f" '{self._RESOURCE.__name__}', "
                    f"not '{type(resource)}'. "
                )

    def dump(self, camel_case: bool = False) -> List[Dict[str, Any]]:
        """Dump the instance into a json serializable Python data type.

        Args:
            camel_case (bool): Use camelCase for attribute names. Defaults to False.

        Returns:
            List[Dict[str, Any]]: A list of dicts representing the instance.
        """
        return [resource.dump(camel_case=camel_case) for resource in self.data]

    def to_pandas(self, camel_case=True) -> DataFrame:
        return DataFrame(self.dump(camel_case=camel_case))

    def _repr_html_(self):
        return self.to_pandas(camel_case=True)._repr_html_()

    def __getitem__(self, item):
        return self.data[item]

    def __iter__(self):
        return self.data.__iter__()

    def __repr__(self):
        return_string = [object.__repr__(d) for d in self.data]
        return f"[{', '.join(r for r in return_string)}]"

    def __len__(self):
        return self.data.__len__()


class WellList(WDLResourceList):
    _RESOURCE = Well


class WellboreList(WDLResourceList):
    _RESOURCE = Wellbore


class SequenceList(WDLResourceList):
    _RESOURCE = GetSequenceDTO


class NPTList(WDLResourceList):
    _RESOURCE = NPT


class TrajectoryList(WDLResourceList):
    _RESOURCE = Trajectory


class TrajectoryDataList(WDLResourceList):
    _RESOURCE = TrajectoryData


class NDSList(WDLResourceList):
    _RESOURCE = NDS


class MeasurementList(WDLResourceList):
    _RESOURCE = SequenceMeasurements


class MeasurementDataList(WDLResourceList):
    _RESOURCE = SequenceGetData
