from __future__ import annotations

from dv_data_generator.interface.display_video import DisplayVideo


class DvRequestTypes:
    LIST_PARTNERS = "LIST_PARTNERS"
    LIST_PARTNER_IDS = "LIST_PARTNER_IDS"


class DvRequestBuilder(DisplayVideo):
    def __init__(self, *args, **kwargs):
        self._query = None
        super(__class__, self).__init__(*args, **kwargs)

    def set_request_type(self, request_type: DvRequestTypes) -> DvRequestBuilder:
        self._query = request_type
        return self

    def execute(self):
        assert self._query != None, "No query has been selected"
        if self._query == DvRequestTypes.LIST_PARTNERS:
            return self.list_partners().data
        if self._query == DvRequestTypes.LIST_PARTNER_IDS:
            return self.list_partners().filter_ids().data

    @property
    def query(self) -> dict:
        return self._query
