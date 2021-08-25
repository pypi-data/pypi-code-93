from __future__ import annotations
from typing import Iterable
from datetime import datetime

from dv_data_generator.interface.double_click_bid_manager import DoubleClickBidManager
from dv_data_generator.helper.assertion import is_list_of_string


class DvReportBuilder(DoubleClickBidManager):
    def __init__(self, *args, **kwargs):
        self._query = {
            "kind": "doubleclickbidmanager#query",
            "metadata": {"format": "CSV", "dataRange": "CURRENT_DAY"},
            "timezoneCode": "Europe/Amsterdam",
            "params": {
                "type": "TYPE_GENERAL",
                "options": {"includeOnlyTargetedUserLists": False},
            },
            "schedule": {"frequency": "ONE_TIME"},
        }
        super(__class__, self).__init__(*args, **kwargs)

    def __datetime_to_timestamp(self, input_datetime):
        return round(input_datetime.timestamp() * 1000)

    def set_title(self, title: str) -> DvReportBuilder:
        assert isinstance(
            title, str), "title must be a string, preferably with a uuid"

        self._query["metadata"]["title"] = title

        return self

    def set_partner_filter(self, partners: Iterable[str]) -> DvReportBuilder:
        """Sets the partner id's as a filter to the report

        Args:
            partners (Iterable[str]): list of string partner id's

        Returns:
            DvReportBuilder: self for function chaining
        """
        assert is_list_of_string(
            partners), "partners must be a list of strings"

        filters = []
        for partner in partners:
            filters.append({"type": "FILTER_PARTNER", "value": partner})

        self._query["params"]["filters"] = filters
        return self

    def set_advertiser_filters(self, advertisers: Iterable[str]) -> DvReportBuilder:
        assert is_list_of_string(
            advertisers), "advertisers must be a list of strings"

        filters = []
        for advertiser in advertisers:
            filters.append({"type": "FILTER_ADVERTISER", "value": advertiser})

        self._query["params"]["filters"] = filters
        return self

    def set_dimensions(self, dimensions: Iterable[str]) -> DvReportBuilder:
        assert is_list_of_string(
            dimensions), "dimensions must be a list of strings"

        self._query["params"]["groupBys"] = dimensions

        return self

    def set_metrics(self, metrics: Iterable[str]) -> DvReportBuilder:
        assert is_list_of_string(metrics), "metrics must be a list of strings"

        self._query["params"]["metrics"] = metrics

        return self

    def set_timeframe(
        self, start_date: datetime, end_date: datetime
    ) -> DvReportBuilder:
        assert isinstance(
            start_date, datetime), "start_date must be a datetime"
        assert isinstance(end_date, datetime), "end_date must be a datetime"

        self._query["reportDataStartTimeMs"] = self.__datetime_to_timestamp(
            start_date
        )
        self._query["reportDataEndTimeMs"] = self.__datetime_to_timestamp(
            end_date
        )

        self._query["metadata"]["dataRange"] = "CUSTOM_DATES"

        return self

    def execute(self):
        return super().execute_query(self._query).data

    @property
    def query(self) -> dict:
        return self._query
