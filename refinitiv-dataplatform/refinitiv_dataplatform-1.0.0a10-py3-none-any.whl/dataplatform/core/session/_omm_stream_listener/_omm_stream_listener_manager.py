# coding: utf-8

###############################################################
#
#   IMPORTS
#
__all__ = ["OMMStreamObserver"]

###############################################################
#
#   STANDARD IMPORTS
#

import logging

###############################################################
#
#   REFINITIV IMPORTS
#

from refinitiv.dataplatform.delivery.stream import OMMItemStream


###############################################################
#
#   CLASS DEFINITIONS
#
class OMMStreamObserver:
    def __init__(self, session):
        self._session = session
        self._all_omm_item_stream = dict()
        self._all_omm_stream_listeners = dict()

    def close_all_omm_streams(self):
        for listener in self._all_omm_stream_listeners.values():
            self._unsubscribe_omm_stream(listener)

    #############################################################
    # Manages Listeners for OMMStream
    #############################################################
    def _subscribe_omm_stream(self, omm_stream_listener, with_updates=True):
        if omm_stream_listener.id is None:
            omm_stream_listener._id = self._get_new_id()

        if omm_stream_listener.id in self._all_omm_item_stream:
            # Remove existing OMMItemStream
            omm_item_stream = self._all_omm_item_stream.pop(omm_stream_listener.id)
            self._all_omm_stream_listeners.pop(omm_item_stream.stream_id)
            omm_item_stream.close()
            del omm_item_stream

        omm_item_stream = OMMItemStream(
            session=self,
            name=omm_stream_listener.name,
            domain=omm_stream_listener.domain,
            service=omm_stream_listener.service,
            fields=omm_stream_listener.fields,
            on_refresh=self.__on_refresh_omm_stream,
            on_update=self.__on_update_omm_stream,
            on_status=self.__on_status_omm_stream,
            on_complete=self.__on_complete_omm_stream,
            on_error=self.__on_error_omm_stream,
        )
        # Register omm_stream before opening to link listener to stream
        self._all_omm_item_stream[omm_stream_listener.id] = omm_item_stream

        self._session._register_stream(omm_item_stream)
        if omm_stream_listener.id not in self._all_omm_stream_listeners:
            self._all_omm_stream_listeners[
                omm_item_stream.stream_id
            ] = omm_stream_listener

        self.__dump_omm_stream_listener_info()

        state = omm_item_stream.open(with_updates=with_updates)
        return state

    async def _subscribe_omm_stream_async(self, omm_stream_listener, with_updates=True):
        if omm_stream_listener.id is None:
            omm_stream_listener._id = self._get_new_id()
        if omm_stream_listener.id in self._all_omm_item_stream:
            # Remove existing OMMItemStream
            omm_item_stream = self._all_omm_item_stream.pop(omm_stream_listener.id)
            self._all_omm_stream_listeners.pop(omm_item_stream.stream_id)
            omm_item_stream.close()
            del omm_item_stream

        omm_item_stream = OMMItemStream(
            session=self,
            name=omm_stream_listener.name,
            domain=omm_stream_listener.domain,
            service=omm_stream_listener.service,
            fields=omm_stream_listener.fields,
            on_refresh=self.__on_refresh_omm_stream,
            on_update=self.__on_update_omm_stream,
            on_status=self.__on_status_omm_stream,
            on_complete=self.__on_complete_omm_stream,
            on_error=self.__on_error_omm_stream,
        )
        if omm_stream_listener.id not in self._all_omm_stream_listeners:
            self._all_omm_stream_listeners[
                omm_item_stream.stream_id
            ] = omm_stream_listener
        self._all_omm_item_stream[omm_stream_listener.id] = omm_item_stream

        self.__dump_omm_stream_listener_info()

        state = await omm_item_stream.open_async(with_updates=with_updates)
        return state

    def __check_omm_stream_listener(self, omm_stream_listener):
        if omm_stream_listener is None:
            raise AttributeError("omm_stream_listener is None.")

        if omm_stream_listener.id is None:
            raise AttributeError("omm_stream_listener was not subscribed.")
        elif omm_stream_listener.id not in self._all_omm_item_stream:
            raise AttributeError(
                f"omm_stream_listener {omm_stream_listener.id} was not found."
            )
        return True

    def _check_omm_item_stream(self, omm_item_stream):
        if omm_item_stream is None:
            return False
        elif omm_item_stream.stream_id is None:
            # search if omm_item_stream is stored in self._all_omm_stream_listeners
            return omm_item_stream in self._all_omm_item_stream.values()
        else:
            return omm_item_stream.stream_id in self._all_omm_stream_listeners

    def _unsubscribe_omm_stream(self, omm_stream_listener):
        if self.__check_omm_stream_listener(omm_stream_listener):
            omm_item_stream = self._all_omm_item_stream[omm_stream_listener.id]
            self._all_omm_stream_listeners.pop(omm_item_stream.stream_id)
            omm_item_stream.close()
            self._all_omm_item_stream.pop(omm_stream_listener.id)

    async def __unsubscribe_omm_stream_async(self, omm_stream_listener):
        if self.__check_omm_stream_listener(omm_stream_listener):
            omm_item_stream = self._all_omm_item_stream[omm_stream_listener.id]
            self._all_omm_stream_listeners.pop(omm_item_stream.stream_id)
            await omm_item_stream.close_async()
            self._all_omm_item_stream.pop(omm_stream_listener.id)

    def __dump_omm_stream_listener_info(self, omm_stream=None):
        if False:
            print(f"All omm streams : {self._all_stream_subscriptions}")
            if omm_stream:
                print(
                    f"{omm_stream.stream_id} in all omm streams : {omm_stream.stream_id in self._all_omm_item_stream}"
                )
            print(f"All omm stream listeners : {self._all_omm_stream_listeners}")
            print("OMM Streams :")
            for i, item in self._all_omm_item_stream.items():
                print(f"\t{i} - {item.name} - {item.stream_id}")
            print("OMM stream listeners :")
            for i, item in self._all_omm_stream_listeners.items():
                print(f"\t{i} - {item.name} - {item.id}")

    # Callbacks for OMMStreamListener

    def __on_refresh_omm_stream(self, omm_stream, message):
        self.__dump_omm_stream_listener_info(omm_stream)
        if omm_stream:
            if omm_stream.stream_id in self._all_omm_stream_listeners:
                listener = self._all_omm_stream_listeners[omm_stream.stream_id]
                try:
                    listener.on_refresh(listener, message)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_refresh user function on stream {listener.id} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received refresh message from unknown stream {omm_stream.stream_id}",
                )
        else:
            self.log(logging.ERROR, "Received refresh message from None stream")

    def __on_update_omm_stream(self, omm_stream, update):
        if omm_stream:
            if omm_stream.stream_id in self._all_omm_stream_listeners:
                listener = self._all_omm_stream_listeners[omm_stream.stream_id]
                try:
                    listener.on_update(listener, update)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_update user function on stream {listener.id} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received update message from unknown stream {omm_stream.stream_id}",
                )
        else:
            self.log(logging.ERROR, "Received update message from None stream")

    def __on_complete_omm_stream(self, omm_stream):
        self.__dump_omm_stream_listener_info(omm_stream)
        if omm_stream:
            if omm_stream.stream_id in self._all_omm_stream_listeners:
                listener = self._all_omm_stream_listeners[omm_stream.stream_id]
                try:
                    listener.on_complete(listener)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_complete user function on stream {listener.id} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received complete message from unknown stream {omm_stream.stream_id}",
                )
        else:
            self.log(logging.ERROR, "Received refresh complete from None stream")

    def __on_status_omm_stream(self, omm_stream, status):
        self.__dump_omm_stream_listener_info(omm_stream)
        if omm_stream:
            if omm_stream.stream_id in self._all_omm_stream_listeners:
                listener = self._all_omm_stream_listeners[omm_stream.stream_id]
                try:
                    listener.on_status(listener, status)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_status user function on stream {listener.id} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received refresh status from unknown stream {omm_stream.stream_id}",
                )
        else:
            self.log(logging.ERROR, "Received refresh status from None stream")

    def __on_error_omm_stream(self, omm_stream, error):
        self.__dump_omm_stream_listener_info(omm_stream)
        if omm_stream:
            if omm_stream.stream_id in self._all_omm_stream_listeners:
                listener = self._all_omm_stream_listeners[omm_stream.stream_id]
                try:
                    listener.on_error(listener, error)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_error user function on stream {listener.id} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received error message from unknown stream {omm_stream.stream_id}",
                )
        else:
            self.log(logging.ERROR, "Received error message from None stream")
