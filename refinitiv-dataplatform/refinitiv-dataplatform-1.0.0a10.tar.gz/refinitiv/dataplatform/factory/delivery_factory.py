# coding: utf8

from ..delivery.stream.stream import Stream
from ..delivery.stream.omm_item_stream import OMMItemStream
from ..delivery.data.endpoint import Endpoint

__all__ = ["DeliveryFactory"]


class DeliveryFactory:
    @staticmethod
    def create_stream(stream_params):
        if isinstance(stream_params, OMMItemStream.Params):
            return DeliveryFactory.create_item_stream(
                stream_params._session,
                stream_params._name,
                stream_params._fields,
                stream_params._service,
                stream_params._domain,
                stream_params._extended_params,
                stream_params._on_refresh_cb,
                stream_params._on_update_cb,
                stream_params._on_status_cb,
                stream_params._on_complete_cb,
            )
        return None

    @staticmethod
    def create_item_stream(
        session,
        name,
        fields=None,
        service=None,
        domain="MarketPrice",
        extended_params=None,
        on_refresh=None,
        on_update=None,
        on_status=None,
        on_complete=None,
    ):
        item_stream_params = OMMItemStream.Params(
            session=session,
            name=name,
            fields=fields,
            service=service,
            domain=domain,
            extended_params=extended_params,
            on_refresh=on_refresh,
            on_update=on_update,
            on_status=on_status,
            on_complete=on_complete,
        )
        return OMMItemStream(
            item_stream_params._session,
            item_stream_params._name,
            domain=item_stream_params._domain,
            service=item_stream_params._service,
            fields=item_stream_params._fields,
            extended_params=item_stream_params._extended_params,
            on_refresh=item_stream_params._on_refresh_cb,
            on_status=item_stream_params._on_status_cb,
            on_update=item_stream_params._on_update_cb,
            on_complete=item_stream_params._on_complete_cb,
        )

    @staticmethod
    def create_end_point_with_params(endpoint_params):
        if isinstance(endpoint_params, Endpoint.Params):
            return Endpoint(
                endpoint_params.session,
                endpoint_params.url,
                endpoint_params.on_response,
            )

    @staticmethod
    def create_end_point(session, url, on_response=None):
        endpoint_params = Endpoint.Params(
            session=session, url=url, on_response=on_response
        )
        return DeliveryFactory.create_end_point_with_params(endpoint_params)
