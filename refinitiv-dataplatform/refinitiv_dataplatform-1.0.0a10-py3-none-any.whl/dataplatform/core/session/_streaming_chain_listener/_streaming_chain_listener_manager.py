# coding: utf-8

###############################################################
#
#   IMPORTS
#
__all__ = ["StreamingChainObserver"]

###############################################################
#
#   STANDARD IMPORTS
#
import logging

###############################################################
#
#   REFINITIV IMPORTS
#


###############################################################
#
#   CLASS DEFINITIONS
#


class StreamingChainObserver:
    def __init__(self, session):
        self._session = session
        self._all_streaming_chains = dict()
        self._all_chains_listeners = dict()

    def close_all_streaming_chains(self):
        for listener in self._all_chains_listeners.values():
            self._unsubscribe_streaming_chain(listener)

    #############################################################
    # Manages Listeners for StreamingChain
    #############################################################

    def _subscribe_streaming_chain(self, chain_listener, with_updates=True):
        from refinitiv.dataplatform.content.streaming.streamingchain import (
            StreamingChain,
        )

        if chain_listener is None:
            raise Exception("Try to subscribe a None listener")

        if chain_listener.name in self._all_streaming_chains:
            # Restart the StreamingChain
            streaming_chain = self._all_streaming_chains[chain_listener.name]
            streaming_chain.close()
        else:
            streaming_chain = StreamingChain(
                name=chain_listener.name,
                session=self,
                service=chain_listener.service,
                skip_summary_links=chain_listener.skip_summary_links,
                skip_empty=chain_listener.skip_empty,
                override_summary_links=chain_listener.override_summary_links,
                on_add=self.__on_add_streaming_chain,
                on_remove=self.__on_remove_streaming_chain,
                on_update=self.__on_update_streaming_chain,
                on_complete=self.__on_complete_streaming_chain,
                on_error=self._on_error_streaming_chain,
            )
            self._all_streaming_chains[chain_listener.name] = streaming_chain
            self._all_chains_listeners[streaming_chain.name] = chain_listener

        self.__dump_chain_listener_info()

        constituents = streaming_chain.open(with_updates=with_updates)
        return constituents

    async def _subscribe_streaming_chain_async(self, chain_listener, with_updates=True):
        from refinitiv.dataplatform.content.streaming.streamingchain import (
            StreamingChain,
        )

        if chain_listener is None:
            raise Exception("Try to subscribe a None listener")

        if chain_listener.name in self._all_streaming_chains:
            # Restart the StreamingChain
            self._all_streaming_chains[chain_listener.name].close()
        else:
            streaming_chain = StreamingChain(
                session=self,
                name=chain_listener.name,
                service=chain_listener.service,
                skip_summary_links=chain_listener.skip_summary_links,
                skip_empty=chain_listener.skip_empty,
                override_summary_links=chain_listener.override_summary_links,
                on_add=self.__on_add_streaming_chain,
                on_remove=self.__on_remove_streaming_chain,
                on_update=self.__on_update_streaming_chain,
                on_complete=self.__on_complete_streaming_chain,
                on_error=self._on_error_streaming_chain,
            )
            self._all_streaming_chains[chain_listener.name] = streaming_chain
            self._all_chains_listeners[streaming_chain.name] = chain_listener

        self.__dump_chain_listener_info()

        constituents = await streaming_chain.open_async(with_updates=with_updates)
        return constituents

    def __check_streaming_chain_listener(self, chain_listener):
        if chain_listener is None:
            raise AttributeError("chain_listener is None.")

        if chain_listener.name not in self._all_chains_listeners:
            raise AttributeError(
                f"chain listener '{chain_listener.name}' was not found."
            )
        return True

    def _unsubscribe_streaming_chain(self, chain_listener):
        if self.__check_streaming_chain_listener(chain_listener):
            streaming_chain = self._all_streaming_chains[chain_listener.name]
            self._all_chains_listeners.pop(chain_listener.name)
            streaming_chain.close()
            self._all_streaming_chains.pop(chain_listener.name)

    async def _unsubscribe_streaming_chain_async(self, chain_listener):
        if self.__check_omm_stream_listener(chain_listener):
            streaming_chain = self._all_streaming_chains[chain_listener.name]
            self._all_chains_listeners.pop(chain_listener.name)
            await streaming_chain.close_async()
            self._all_streaming_chains.pop(chain_listener.name)

    def __dump_chain_listener_info(self, streaming_chain=None):
        if False:
            print("##########################################")
            print("Dump streaming chain listener")
            print(f"All streaming chains : {list(self._all_streaming_chains)}")
            if streaming_chain is not None:
                print(
                    f"{streaming_chain.name} in all streaming chains : {streaming_chain.name in self._all_streaming_chains}"
                )
                print(
                    f"{streaming_chain.name} in all chain listeners: {streaming_chain.name in self._all_chains_listeners}"
                )
            print("Chain listeners :")
            for name, item in self._all_chains_listeners.items():
                print(f"\t{name} - {item}")
            print("Streaming Chains :")
            for name, item in self._all_streaming_chains.items():
                print(f"\t{name} - {item}")
            print("##########################################")

    # Callbacks for StreamingChainListener
    def __on_add_streaming_chain(self, streaming_chain, index, constituent):
        assert streaming_chain is not None
        if streaming_chain.name in self._all_streaming_chains:
            if streaming_chain.name in self._all_chains_listeners:
                listener = self._all_chains_listeners[streaming_chain.name]
                try:
                    listener.on_add(streaming_chain, index, constituent)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_add user function on streaming chain {streaming_chain.name} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received add message from unknown streaming chain {streaming_chain.name}",
                )
        else:
            self.log(
                logging.ERROR,
                f"Received add message from unknown streaming chain {streaming_chain.name}",
            )

    def __on_remove_streaming_chain(self, streaming_chain, index, constituent):
        assert streaming_chain is not None
        if streaming_chain.name in self._all_streaming_chains:
            if streaming_chain.name in self._all_chains_listeners:
                listener = self._all_chains_listeners[streaming_chain.name]
                try:
                    listener.on_remove(streaming_chain, index, constituent)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_remove user function on stream {streaming_chain.name} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received remove message from unknown streaming chain {streaming_chain.name}",
                )
        else:
            self.log(
                logging.ERROR, "Received refresh message from None streaming chain"
            )

    def __on_update_streaming_chain(
        self, streaming_chain, index, old_constituent, new_constituent
    ):
        assert streaming_chain is not None
        if streaming_chain.name in self._all_streaming_chains:
            if streaming_chain.name in self._all_chains_listeners:
                listener = self._all_chains_listeners[streaming_chain.name]
                try:
                    listener.on_update(
                        streaming_chain, index, old_constituent, new_constituent
                    )
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_update user function on streaming chain {streaming_chain.name} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received update message from unknown stream {streaming_chain.name}",
                )
        else:
            self.log(logging.ERROR, "Received update message from None stream")

    def __on_complete_streaming_chain(self, streaming_chain, constituents):
        assert streaming_chain is not None
        if streaming_chain.name in self._all_streaming_chains:
            if streaming_chain.name in self._all_chains_listeners:
                listener = self._all_chains_listeners[streaming_chain.name]
                try:
                    listener.on_complete(streaming_chain, constituents)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_complete user function on streaming chain {name} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received complete message from unknown streaming chain {name}",
                )
        else:
            self.log(
                logging.ERROR, "Received complete message from None streaming chain"
            )

    def _on_error_streaming_chain(self, streaming_chain, chain_record_name, error):
        assert streaming_chain is not None
        self.__dump_chain_listener_info(streaming_chain)
        if streaming_chain.name in self._all_streaming_chains:
            if streaming_chain.name in self._all_chains_listeners:
                listener = self._all_chains_listeners[streaming_chain.name]
                try:
                    listener.on_error(streaming_chain, chain_record_name, error)
                except Exception as e:
                    self.log(
                        logging.ERROR,
                        f"on_error user function on streaming chain {streaming_chain.name} raised error {e}",
                    )
            else:
                self.log(
                    logging.ERROR,
                    f"Received error message from unknown streaming chain {streaming_chain.name}",
                )
        else:
            self.log(logging.ERROR, "Received error message from None streaming chain")
