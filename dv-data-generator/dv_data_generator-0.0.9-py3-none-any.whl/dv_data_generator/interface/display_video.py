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

    def list_partners(self) -> DisplayVideo:
        partners = []
        next_page_token = ""

        while next_page_token != None:
            try:
                result = self.__list_partners_page(next_page_token)

                partners = [*result.get("partners", []), *partners]

                next_page_token = result.get("nextPageToken", None)
            except Exception as e:
                next_page_token = None

        self._data = partners
        return self

    def filter_ids(self) -> DisplayVideo:
        self.list_partners()
        partner_ids = [partner.get("partnerId") for partner in self._data]
        self._data = partner_ids
        return self

    @property
    def data(self) -> list:
        """A list containing the endpoint data

        Returns:
             list: Report data in a dataframe
        """
        return self._data
