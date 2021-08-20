__all__ = ["ChainRecords"]

from threading import Lock

from refinitiv.dataplatform.delivery.stream import OMMItemStream, StreamState
from refinitiv.dataplatform.core.log_reporter import LogReporter


class ChainRecords(LogReporter):
    def __init__(self, streaming_chain, session):

        super().__init__(logger=session)

        self._stream_chain = streaming_chain
        self._session = session

        # mapping chain record name to chain record
        self.records_by_name = {}

        # mapping chain record name to each chain record item stream
        self.statuses_by_name = {}

        # dictionary mapping between chain record name and future object
        self.refreshing_by_name = {}

        # mapping dict of each streaming chains to construct this given chain
        # note that completed chain record may construct from multiple chain records
        # ie. complete chain record named ".DJI" contains with three chain records including
        # "0#.DJI", "1#.DJI", "2#.DJI"
        self.streams_by_name = {}

        self.lock = {
            "streams": Lock(),
            "refreshing": Lock(),
            "records": Lock(),
            "statuses": Lock(),
        }

    def add(self, name):
        """
        Construct new item streaming for given chain record name
        and store it as a mapping from chain record name
        """
        with self.lock["streams"]:
            assert name not in self.streams_by_name

        from .streaming_chain import _STREAMING_DOMAIN, _STREAMING_FIELDS

        # construct and run the item stream
        stream = OMMItemStream(
            session=self._session,
            name=name,
            domain=_STREAMING_DOMAIN,
            service=self._stream_chain._service,
            fields=_STREAMING_FIELDS,
            on_refresh=self._stream_chain._on_refresh_handler,
            on_status=self._stream_chain._on_status_handler,
            on_update=self._stream_chain._on_update_handler,
            on_complete=self._stream_chain._on_complete_handler,
            on_error=self._stream_chain._on_error_handler,
        )

        # store the mapping between chain record name to stream
        with self.lock["streams"]:
            self.streams_by_name[name] = stream

        with self.lock["refreshing"]:
            self.refreshing_by_name[
                name
            ] = self._session._loop.create_future()  # asyncio.Future()

        # done, return this chain record item stream
        return stream

    def has(self, name):
        """ Check given chain record has chain record object or not ? """
        with self.lock["records"]:
            return name in self.records_by_name

    def has_stream(self, name):
        """ Check given chain record has item stream or not ? """
        with self.lock["streams"]:
            return name in self.streams_by_name

    def not_has_stream(self, name):
        return not self.has_stream(name)

    def get_display_name(self, name):
        # get the first chain display name and return
        with self.lock["records"]:
            # check for chain record name is valid or not?
            chain_record = self.records_by_name[name]
            return chain_record.displayName or ""

    async def open_streams(self, with_updates):
        # loop over all initial set of stream for this chains and open it
        with self.lock["streams"]:
            for name in self.streams_by_name.keys():
                # open each chain record stream
                await self.open_stream(name, with_updates)

    async def open_stream(self, name, with_updates):
        self.info(f"Opening stream of chain record = {name}.")
        stream = self.streams_by_name[name]
        await stream.open_async(with_updates=with_updates)

    def is_status_closed(self, name):
        # warning THIS IS A HACK. THE STREAMING CHAIN NEED TO REFACTOR FOLLOWING THE NEW DESIGN OF STREAMING WEBSOCKET
        if name not in self.statuses_by_name:
            return False

        status = self.statuses_by_name[name].get("status", None)
        return status == StreamState.Closed if status is not None else False

    async def wait_refresh(self, name):
        await self.refreshing_by_name[name]

    def get_record(self, name):
        with self.lock["records"]:
            item = self.records_by_name.get(name, None)
        return item

    def get_stream(self, name):
        return self.streams_by_name[name]

    def close_streams(self):
        """ close chain record item streams """
        # loop over all initial set of stream for this chains and close it
        with self.lock["streams"]:
            for name, stream in self.streams_by_name.items():
                # close each chain record stream
                self.info(f"Closing stream of chain record = {name}.")
                stream.close()

    def add_record(self, name, record):
        #   store in the mapping between streaming name to chain record
        with self.lock["records"]:
            assert name not in self.records_by_name
            self.records_by_name[name] = record

    def refreshed(self, name):
        # change future flag on this chain record stream
        with self.lock["refreshing"]:
            refreshing = self.refreshing_by_name[name]
            # warning :: PREVENT AND ERROR WHEN IT HAS MULTIPLE REFRESH MESSAGE FROM SERVER
            #            PLEASE RECHECK THE PROTOCOL ON SERVER SIDE
            if not refreshing.done():
                # it's possible that it's receiving a refresh message multiple time from server
                self._session._loop.call_soon_threadsafe(refreshing.set_result, True)

    def set_status(self, name, status):
        # store the status of chain record streaming
        with self.lock["statuses"]:
            self.statuses_by_name[name] = status
