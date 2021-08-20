from datetime import date
from enum import Enum
from typing import List, Optional

from kpler.sdk import Platform
from kpler.sdk.client import KplerClient
from kpler.sdk.configuration import Configuration
from kpler.sdk.helpers import (
    process_date_parameter,
    process_enum_parameter,
    process_enum_parameters,
    process_list_parameter,
)


class FleetUtilizationVessels(KplerClient):

    """
    The ``FleetUtilizationVessels`` provides current and historical supply & demand capacity balance, total,loaded & ballast capacity evolution and capacity available by products.
    """

    RESOURCE_NAME = "fleet-utilization/vessels"

    AVAILABLE_PLATFORMS = [Platform.Dry, Platform.Liquids, Platform.LNG, Platform.LPG]

    def __init__(self, configuration: Configuration, column_ids: bool = True, log_level=None):
        super().__init__(configuration, self.AVAILABLE_PLATFORMS, column_ids, log_level)

    def get(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        zones: Optional[List[str]] = None,
        products: Optional[List[str]] = None,
        vessel_types_cpp: Optional[List[Enum]] = None,
        vessel_types_oil: Optional[List[Enum]] = None,
        vessel_states: Optional[List[Enum]] = None,
        unit: Optional[Enum] = None,
        size: Optional[int] = None,
        gte: Optional[int] = None,
        lte: Optional[int] = None,
        vessel_types: Optional[List[Enum]] = None,
    ):

        """
        Args:
            start_date: Optional[date] Start of the period (YYYY-MM-DD)
            end_date: Optional[date] End of the period (YYYY-MM-DD)
            zones: Optional[List[str]] Names of countries/geographical zones
            products: Optional[List[str]] Names of products
            vessel_types_cpp: Optional[List[Enum]] ``VesselTypesCPP``
            vessel_types_oil: Optional[List[Enum]] ``VesselTypesOil``
            vessel_states: Optional[List[Enum]] ``FleetUtilizationVesselsState``
            unit: Optional[Enum] ``FleetUtilizationVesselsUnit``
            size: Optional[int] Maximum number of fleet utilization vessels returned
            gte: Optional[int] Get vessels with deadweight/capacity greater or equals to this value by default 0
            lte: Optional[int] Get vessels with deadweight/capacity lower or equals to this value by default 606550
            vessel_types: Optional[List[Enum]] ``VesselTypesDry`` ``VesselTypesLNG`` ``VesselTypesLPG``

        Examples:
            >>> from datetime import date
            ... from kpler.sdk.resources.fleet_utilization_vessels import FleetUtilizationVessels
            ... from kpler.sdk import FleetUtilizationVesselsState
            ... fleet_utilization_vessels_client=FleetUtilizationVessels(config)
            ... fleet_utilization_vessels_client.get(
            ...     start_date=date(2020,10,1),
            ...     end_date=date(2020,11,1),
            ...     zones=["Japan"],
            ...     products=["gasoline", "DPP"],
            ...    vessel_states=[FleetUtilizationVesselsState.Loaded],
            ...     size=5
            ... )

            .. csv-table::
                :header:  "Date (timestamp)","IMO","Name","Dead Weight Tonnage","Vessel Type","Vessel State","Current Zone","Last Product on board"

                "2020-10-01","9751121","Kakusho Iii","3500","GP","Loaded","Japan","DPP"
                "2020-10-01","9774410","Sun Venus","6879","GP","Loaded","Japan","DPP"
                "2020-10-01","9524475","Suez Rajan","158574","LR3","Loaded","Japan","DPP"
                "2020-10-01","9636644","Maersk Aegean","37538","MR","Loaded","Japan","DPP"
                "2020-10-01","9346873","Mare Oriens","110295","LR2","Loaded","Japan","DPP"
        """

        query_parameters = {
            "startDate": process_date_parameter(start_date),
            "endDate": process_date_parameter(end_date),
            "zones": process_list_parameter(zones),
            "products": process_list_parameter(products),
            "vesselTypesCpp": process_enum_parameters(vessel_types_cpp, False),
            "vesselTypesOil": process_enum_parameters(vessel_types_oil, False),
            "vesselStates": process_enum_parameters(vessel_states, False),
            "unit": process_enum_parameter(unit),
            "size": size,
            "gte": gte,
            "lte": lte,
            "vesselTypes": process_enum_parameters(vessel_types),
        }
        return self._get_dataframe(self.RESOURCE_NAME, query_parameters)
