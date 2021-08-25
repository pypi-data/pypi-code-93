from __future__ import annotations

from dv_data_generator.helper.google_api import GoogleApi


class DisplayVideo(GoogleApi):
    def __init__(self, *args, **kwargs):
        super(__class__, self).__init__(*args, **kwargs)
        self._data = []
        self._service = self.get_service("DV360")
        self._query = None

    def __list_partners_page(self, next_page_token):
        return self._service.partners().list(pageToken=next_page_token).execute()

    def __list_advertisers_page(self, partner_id, next_page_token):
        return self._service.advertisers().list(partnerId=partner_id, pageToken=next_page_token).execute()

    def __list_lineitems_page(self, advertiser_id, entity_status, next_page_token):
        return self._service.advertisers().lineItems().list(advertiserId=advertiser_id, filter=f'entityStatus="{entity_status}"', pageToken=next_page_token).execute()

    def list_partners(self) -> DisplayVideo:
        partners = []
        next_page_token = ""

        while next_page_token != None:
            result = self.__list_partners_page(next_page_token)
            partners = [*result.get("partners", []), *partners]
            next_page_token = result.get("nextPageToken", None)
            next_page_token = next_page_token if next_page_token != "" else None

        self._data = partners
        return self

    def list_advertisers(self, partner_id) -> DisplayVideo:
        advertisers = []
        next_page_token = ""

        while next_page_token != None:
            result = self.__list_advertisers_page(
                partner_id,
                next_page_token
            )
            advertisers = [*result.get("advertisers", []), *advertisers]
            next_page_token = result.get("nextPageToken", None)
            next_page_token = next_page_token if next_page_token != "" else None

        self._data = advertisers
        return self

    def list_lineitems(self, advertiser_id, entity_status) -> DisplayVideo:
        lineitems = []
        next_page_token = ""

        while next_page_token != None:
            result = self.__list_lineitems_page(
                advertiser_id,
                entity_status,
                next_page_token
            )
            lineitems = [*result.get("lineItems", []), *lineitems]
            next_page_token = result.get("nextPageToken", None)
            next_page_token = next_page_token if next_page_token != "" else None

        self._data = lineitems
        return self

    def filter_ids(self, key) -> DisplayVideo:
        partner_ids = [partner.get(key) for partner in self._data]
        self._data = partner_ids
        return self

    @property
    def data(self) -> list:
        """A list containing the endpoint data

        Returns:
             list: Report data in a dataframe
        """
        return self._data
