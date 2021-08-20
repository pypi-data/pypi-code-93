# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import collections

###############################################################
#
#   REFINITIV IMPORTS
#

###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASS DEFINITIONS
#


class TradeDataStreamCache(object):
    """ cache for trading data stream including order summary and order event """

    #   default cache size
    #       order summary
    _DefaultOrderSummaryCacheSize = 1000
    #       order events
    _DefaultOrderEventsCacheSize = 1000

    def __init__(
        self, session: object, max_order_summary_cache: int, max_order_events_cache: int
    ):
        self._session = session

        #   cache size
        #       order summary
        self._max_order_summary_cache = (
            max_order_summary_cache
            if max_order_summary_cache is not None
            else self._DefaultOrderSummaryCacheSize
        )
        #       order events
        self._max_order_events_cache = (
            max_order_events_cache
            if max_order_events_cache is not None
            else self._DefaultOrderEventsCacheSize
        )

        #   header
        self._order_summary_header_names = None

        #   cache
        #       order summary
        self._order_summary_dict = collections.OrderedDict()
        #       order events
        self._order_key_to_event_list = {}

    def _clear_caches(self):
        """ clear the order summary and order events caches """
        self._order_summary_dict = collections.OrderedDict()
        self._order_key_to_event_list = {}

    def _add_order_summary(self, key, order_summary: list):
        """ add or update the order summary """

        #   check for cache enable or not?
        if self._max_order_summary_cache == 0:
            #   skip
            return

        #   check for update the old order summary
        if key in self._order_summary_dict:
            #   remove old order summary before add the new one
            #       this for the last update order summary in the dict
            del self._order_summary_dict[key]

        #   check the cache size
        if len(self._order_summary_dict) + 1 > self._max_order_summary_cache:
            #   the data exceeds cache size, so remove oldest data in cache
            self._order_summary_dict.popitem(last=False)

        #   add or update the order summary
        self._order_summary_dict[key] = order_summary

        assert len(self._order_summary_dict) <= self._max_order_summary_cache

    def _update_order_summary(self, key, order_summary: dict):
        assert "key" in order_summary
        assert "OrderKey" not in order_summary

        #   check for cache enable or not?
        if self._max_order_summary_cache == 0:
            #   skip
            return

        #   get the 'OrderKey'. it use key as a name
        order_summary_order_key = order_summary.pop("key")

        #   update order summary
        for key, value in order_summary.items():
            try:
                index = self._order_summary_header_names.index(key)
            except ValueError:
                self._session.debug(
                    f"#WARNING!!! received no subscribed field name [{key}]"
                )
                continue

            self._order_summary_dict[order_summary_order_key][index] = value

    def _add_order_event(self, order_event: list):
        assert "key" in order_event
        assert "events" in order_event

        #   check for cache enable or not?
        if self._max_order_events_cache == 0:
            #   skip
            return

        #   extract key and event
        #       key
        key = order_event.get("key", None)
        assert key is not None
        assert isinstance(key, str)

        #       events
        events = order_event.get("events", None)
        assert events is not None
        assert isinstance(events, list)

        #   store in cache
        this_order_events = self._order_key_to_event_list.setdefault(
            key, collections.deque(maxlen=self._max_order_events_cache)
        )
        for event in events:
            #   append to the order event list for this key
            this_order_events.append(event)

        #   done

    def get_last_order_events(self):
        """ get the last order events """

        #   do extract all order events
        all_order_events = []
        for order_key in self._order_key_to_event_list.keys():

            this_order_events = self.__get_last_order_event_with_column_name(order_key)
            for this_order_event in this_order_events:
                assert len(this_order_event) == len(self._event_column_names)

                this_order_event_with_order_key = [
                    order_key,
                ] + this_order_event
                all_order_events.append(this_order_event_with_order_key)

        #   done
        return all_order_events

    @property
    def __order_event_data_column_names(self):
        """the different event type has different data object structure:
        Executed:
        {
            "ExecutionId" : "...",
            "ExecutionQuantity" : "...",
            "ExecutionPrice" : "...",
            "ExecutionValue" : "...",
            "LastMarketMIC": "..."
        }

        Accepted / Replaced / UpdatePending
        {
            "OrderQuantity" : "...",
            "LimitPrice" : "...",
            "StopPrice" : "...",
            "DestinationType": "...",
            "AlgoId": "...",
            "TimeInForce": "...",
            "LastCapacity": "..."
        }

        Cancelled / Rejected / CancelPending

        {
            "Reason" : "..."
        }
        """
        return [
            "ExecutionId",
            "ExecutionQuantity",
            "ExecutionPrice",
            "ExecutionValue",
            "LastMarketMIC",  # Executed
            "OrderQuantity",
            "LimitPrice",
            "StopPrice",
            "DestinationType",
            "AlgoId",
            "TimeInForce",
            "LastCapacity",  # Accepted / Replaced / UpdatePending
            "Reason",  # Cancelled / Rejected / CancelPending
        ]

    @property
    def _event_column_names(self):
        event_column_names = [
            "EventTime",
            "OrderId",
            "EventType",
        ]
        event_column_names.extend(self.__order_event_data_column_names)
        return event_column_names

    def __get_last_order_events(self, order_key: str):
        assert order_key in self._order_key_to_event_list
        return self._order_key_to_event_list[order_key]

    def __get_last_order_event_with_column_name(self, order_key: str):
        """return a of the last order event data from given order key.
        note that the order of data data will be matched with event data column name.
        """

        #   extract and return event data
        events = self.__get_last_order_events(order_key)

        #   loop over all event of this order key
        last_order_event_list = []
        for event in events:
            #   extract last event information
            assert "EventTime" in event
            event_time = event["EventTime"]
            assert "OrderId" in event
            order_id = event["OrderId"]
            assert "EventType" in event
            event_type = event["EventType"]
            assert "EventData" in event
            event_data = event["EventData"]

            #   this order event column name
            this_order_event_column_names = [
                event_data.get(column_name, None)
                for column_name in self.__order_event_data_column_names
            ]

            #   reformat the the event data with column name
            this_event_list = [
                event_time,
                order_id,
                event_type,
            ] + this_order_event_column_names
            last_order_event_list.append(this_event_list)

        #   done
        return last_order_event_list
