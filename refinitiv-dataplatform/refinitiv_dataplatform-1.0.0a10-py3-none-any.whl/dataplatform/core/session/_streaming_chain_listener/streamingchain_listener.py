# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

__all__ = ["StreamingChainListener"]


import abc

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


class StreamingChainListener(abc.ABC):
    """ " This abstract class is designed to let the user to implement streaming chain model.
    Available notifications from the stream are :
        - add
        - remove
        - update
        - complete
        - error
    """

    def __init__(
        self,
        name,
        service=None,
        #   option for chain constituents
        skip_summary_links=True,
        skip_empty=True,
        override_summary_links=None,
    ):
        #   store chain service name
        self._service = service

        #   store chain record name
        self._name = name

        #   store skip summary links and skip empty
        self._skip_summary_links = skip_summary_links
        self._skip_empty = skip_empty

        #   store the override number of summary links
        self._override_summary_links = override_summary_links

    @property
    def service(self):
        return self._service

    @property
    def name(self):
        return self._name

    @property
    def fields(self):
        return self._fields

    @property
    def domain(self):
        return self._domain

    @property
    def id(self):
        return self._id

    @property
    def skip_summary_links(self):
        return self._skip_summary_links

    @property
    def skip_empty(self):
        return self._skip_empty

    @property
    def override_summary_links(self):
        return self._override_summary_links

    ###############################################################
    @property
    def is_chain(self):
        """
        Indicates if requested name is a chain or not.
        This property is available once chain was completely decoded.

        Returns
        -------
        boolean
            True if it is a chain record, otherwise False
        """
        pass

    ###############################################################
    #   callback functions when received messages
    @abc.abstractmethod
    def on_add(self, streaming_chain, index, constituent):
        pass

    @abc.abstractmethod
    def on_remove(self, streaming_chain, index, constituent):
        pass

    @abc.abstractmethod
    def on_update(self, streaming_chain, index, old_constituent, new_constituent):
        pass

    @abc.abstractmethod
    def on_complete(self, streaming_chain, constituents):
        pass

    @abc.abstractmethod
    def on_error(self, streaming_chain, name, error):
        pass
