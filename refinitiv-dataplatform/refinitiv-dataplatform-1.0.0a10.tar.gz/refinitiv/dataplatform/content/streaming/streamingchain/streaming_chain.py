# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#
import re
from threading import Lock

###############################################################
#
#   REFINITIV IMPORTS
#
from refinitiv.dataplatform.delivery.stream import Openable, StreamState

###############################################################
#
#   LOCAL IMPORTS
#
from .chain_records import ChainRecords
from .chain_record import ChainRecord10Chars, ChainRecord17Chars, ChainRecord32Chars
from .display_template import DisplayTemplate
from refinitiv.dataplatform.core.log_reporter import LogReporter

###############################################################
#
#   CLASS DEFINITIONS
#

#   streaming information specific to streaming chain records
#       domain
_STREAMING_DOMAIN = "MarketPrice"
#       service
_STREAMING_SERVICE = "IDN_RDF"
#       field (empty list means all fields)
_STREAMING_FIELDS = []

#   response message from streaming
_FIELDS_KEY_NAME = "Fields"

#   chain record pattern in regular expression format
_CHAIN_RECORD_PATTERN = re.compile(r"^((?P<sequence>[0-9]+)#)*(?P<RIC>[\w\W]+)$")

#   default number of initialize concurrent decode streams
_NUMBER_DECODE_STREAMS = 1


def _get_fields_from_response(response):
    if _FIELDS_KEY_NAME in response:
        fields = response[_FIELDS_KEY_NAME]
    else:
        fields = []
    return fields


class StreamingChain(Openable, LogReporter):
    """
    StreamingChain is designed to request streaming chains and decode it dynamically.
    This class also act like a cache for each part of the chain record.
    """

    def __init__(
        self,
        name,
        session=None,
        service=None,
        # option for chain constituents
        skip_summary_links=True,
        skip_empty=True,
        override_summary_links=None,
        # callbacks
        on_add=None,
        on_remove=None,
        on_update=None,
        on_complete=None,
        on_error=None,
    ):

        #   store session use default session if session doesn't provided
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        self._session = session if session else DefaultSession.get_default_session()

        super().__init__(loop=self._session._loop, logger=self._session)

        self._state = None
        self._events_cache = []

        ########################################################################
        #   chain record properties

        #   store chain record name
        self._name = name
        self._rootChainRecordName = None

        #   service
        self._service = service

        super().__init__(loop=self._session._loop, logger=self._session)

        #   display template of this chain record
        self._displayTemplateLock = Lock()
        self._displayTemplate = None

        #   store a list of decoded constituents
        self._constituentListLock = Lock()
        self._constituentList = None

        ########################################################################
        #   callback functions

        #   store the callback functions from stream
        #       on_add event happen when new constituent added the chain record
        self._on_add = on_add
        self._on_remove = on_remove
        self._on_update = on_update
        self._on_complete = on_complete
        self._on_error = on_error

        ########################################################################
        #   streaming properties

        self._chain_records = ChainRecords(self, self._session)

        #   store is the chain record decode completed or not?
        self._is_complete_decoded = (
            self._session._loop.create_future()
        )  # asyncio.Future()

        #   store the chain record name to the number of offset to this chain record from the root of the chain record
        self._chainRecordNameToNumOffsetsFromRootChainRecordDict = {self._name: 0}

        #   remaining update messages to be processed
        self._remainingUpdateMessageListLock = Lock()
        self._remainingUpdateMessageList = []

        ########################################################################
        #   snapshot properties

        #   store skip summary links and skip empty
        self._skipSummaryLinks = skip_summary_links
        self._skipEmpty = skip_empty

        #   store the override number of summary links
        self._override_summary_links = override_summary_links

        #   this is a mapping between display template to number of summary link
        #       this is used for skip summary link
        self._displayTemplateToNumSummaryLinks = (
            DisplayTemplate.DefaultDisplayTemplateToNumSummaryLinksDict
        )

        #   call an initialize function for constructing the streaming for this chain record
        self._initialize()

    def __repr__(self):
        return f"<{self.__class__.__name__} {self._name}>"

    def __str__(self):
        return f"<{self.__class__.__name__} {self._name}>"

    ###############################################################
    #   properties

    @property
    def _num_summary_links(self):
        """
        Return number of summary links. this could be override by user
        it possible that number of summary links return None if it is a invalid chain record.
        """

        #   get number of summary links from display template
        if self._override_summary_links:
            #   override number of summary links
            return self._override_summary_links
        else:
            #   use the provided number of summary links from display template
            with self._displayTemplateLock:
                return self._displayTemplateToNumSummaryLinks.get(
                    self._displayTemplate, None
                )

    @property
    def name(self):
        return self._name

    @property
    def is_chain(self):
        """Return of this property is blocking until self._is_complete_decoded is done

        Returns
        -------
        boolean
            True if it is a chain record, otherwise False
        """
        return self._session._loop.run_until_complete(self._is_chain_async())
        # if self._is_complete_decoded.done():
        #     return self._session._loop.run_until_complete(self._is_chain_async())
        # else:
        #     return None

    @property
    def summary_links(self):
        """Return of this property is blocking until self._is_complete_decoded is done

        Returns
        -------
        list
            a list of the summary links of this chain record, if the chain record is valid
            otherwise, return empty list
        """

        #   check is this an invalid chain record or not?
        if not self.is_chain:
            #   this is not a chain record, so not constituents, return None
            return None

        #   get number of summary links in this chain record
        num_summary_links = self._num_summary_links

        #   get summary links from stream
        summary_link_list = self._constituentList[:num_summary_links]

        #   do skip None and return
        return [
            summary_link
            for summary_link in summary_link_list
            if not self._skipEmpty or summary_link is not None
        ]

    async def _is_chain_async(self):
        """ This function is used for checking is this a chain or not ? """
        #   wait for until complete received all parts to construct this chain record
        await self._is_complete_decoded

        #   at this point chains are complete received

        return self._chain_records.has(self._name)

    def get_constituents(self):
        """Return of this property is blocking until self._is_complete_decoded is done
            return None, if its is an invalid chain record

        Returns
        -------
        list
            a list of constituents in the chain record, if it is a valid chain record,
            otherwise, return empty list []
        """

        #   check is this an invalid chain record or not?
        if not self.is_chain:
            #   this is not a chain record, so not constituents, return empty list
            #   (don't return None to avoid exception when iterate on StreamingChain)
            return []

        #   get number of summary links in this chain record
        num_summary_links = self._num_summary_links

        #   copy constituents from stream and do skip summary links if skipSummaryLinks is True
        if self._skipSummaryLinks:
            constituent_list = self._constituentList[num_summary_links:]
        else:
            constituent_list = self._constituentList[:]

        #   do skip None and return
        return [
            constituent
            for constituent in constituent_list
            if not self._skipEmpty or constituent is not None
        ]

    def get_display_name(self):
        """
        Returns
        -------
        str
            a value of DSPLY_NAME field if it exist, otherwise empty string
        """
        #   check is this an invalid chain record or not?
        if not self.is_chain:
            # this is not a chain record, so not constituents, return empty string
            return ""

        return self._chain_records.get_display_name(self._name)

    ###############################################################
    #   iterator/getitem functions

    def __iter__(self):
        #   iterate over a snapshot of constituents of this chain record
        yield from self.get_constituents()

    def __getitem__(self, index):
        #   return constituent at given index
        constituent_list = self.get_constituents()
        return constituent_list[index] if constituent_list else None

    def __len__(self):
        return len(self.get_constituents())

    ###############################################################
    #   initialize functions

    def _initialize(self):
        """ initialize the stream for all chain records in the chain record name """

        #   construct the given chain record
        self._chain_records.add(self._name)

        ##################################################
        #   the following steps are an optimization
        #       by construct all possible chain records
        #       when open() is called it will stream parallel all possible chains

        #   match the chain to get RIC and chain sequence number
        matched = re.match(_CHAIN_RECORD_PATTERN, self._name)
        assert matched is not None

        #   get the chain record name
        matched_dict = matched.groupdict()
        self._rootChainRecordName = matched_dict["RIC"]

        #   ready to start the streaming for chain records
        #       this are construct all possible chains
        for i in range(1, _NUMBER_DECODE_STREAMS):
            #   construct the chain record name
            name = r"{}#{}".format(i, self._rootChainRecordName)

            #   construct item stream for this chain record
            self._chain_records.add(name)

    ############################################################
    #   open/close streaming chain functions

    async def _do_open_async(self, with_updates=True):
        """ open all chain record stream and decode it"""
        self._session.info(
            f"StreamingChain :: Processing decode chain record {self._name}."
        )

        await self._chain_records.open_streams(with_updates)

        # check if all chain records were received without error

        ############################################################
        #   now let's start decode given chain record

        #   initialize the list of constituents to be assemble
        with self._constituentListLock:
            self._constituentList = []

        #   initialize the dictionary mapping between chain record name to offset from root of chain recrd
        num_offset_from_root_chain_record = 0

        #   loop until next chain record is None
        name = self._name
        while name:

            # #   store the order for decoding this chain record
            # self._orderedDecodeChainRecordNameList.append(this_chain_record_name)

            #   check this chain are opened for stream or not?
            if self._chain_records.not_has_stream(name):
                #   this chain record doesn't open as streaming yet, so construct the stream and open it
                #   construct chain record stream
                self._chain_records.add(name)

                #   open stream
                await self._chain_records.open_stream(name, with_updates)

            #   wait for this stream response ONLY IF STATUS IS NOT CLOSED
            if self._chain_records.is_status_closed(name):
                #   finished decode chain, so set the complete decoded flags to be False
                self._is_complete_decoded.set_result(False)
            else:
                await self._chain_records.wait_refresh(name)

            #   check this chain record is already open as stream and its chain record is ready or not?
            record = self._chain_records.get_record(name)

            #   check this chain record is valid or not?
            if record:
                #   this is a valid chain record, so get the next chain response chain record

                #   get next chain record for this chain
                name = record.nextChainRecordName

                #   assemble the constituents of the chain record
                for index, constituent in enumerate(record.constituentList):
                    self._append_constituent(
                        num_offset_from_root_chain_record + index, constituent
                    )

                #   store the offset to this chain record
                self._chainRecordNameToNumOffsetsFromRootChainRecordDict[
                    name
                ] = num_offset_from_root_chain_record
                num_offset_from_root_chain_record += record.numConsituents or 0

            else:
                #   something wrong, we should wait for first response from interested chain record stream
                #       and each stream chain should be construct and got response
                #   it's an invalid chain record, so done
                self._session.error(
                    f"StreamingChain :: Stopped to process chain record "
                    f"because it found an invalid chain record {name}."
                )
                self._dispatch_event(
                    self._on_error, name, self._chain_records.get_stream(name).status
                )
                break

            #   done set next chain record to be decoded
            self._session.info(
                f"StreamingChain :: Processing decode next chain record {name}."
            )

        #   finished decode chain, so set the complete decoded flags to be True
        if not self._is_complete_decoded.done():
            self._is_complete_decoded.set_result(True)

        self._dispatch_event(self._on_complete, self.get_constituents())

        #   process remaining update message due to waiting to decode finished
        self._process_remaining_update_messages()

        self._session.info(
            f"StreamingChain :: DONE - Processing decode chain record {self._name}."
        )

        self.state = StreamState.Open

        #  return the list of constituents in this chain
        return self.get_constituents()

    async def _do_close_async(self):
        self._chain_records.close_streams()

    def _do_pause(self):
        # do nothing
        pass

    def _do_resume(self):
        for event_info in self._events_cache:
            callback, args, kwargs = event_info
            self._dispatch_event(callback, *args, **kwargs)

        self._events_cache = []

    ###############################################################
    #   internal processing response chain record functions

    def _process_chain_record(self, name, message):
        """
        This function is designed for processing chain record. this will happen when got the refresh response.
        The processing steps are parsing the response message, request next chain record from stream if it doesn't exist
        """
        self._session.info(
            f"StreamingChain :: Processing response chain record {name}, message = {message}."
        )

        #   get the fields from response message
        fields = _get_fields_from_response(message)

        #   do parse the response message to construct the chain object
        self._parse_chain_record(name, fields)

    def _parse_chain_record(self, name, fields):
        """
        Parse the chain record then construct chain record and store as a mapping between chain record name
        to chain record object.
        """
        self._session.debug(
            f"StreamingChain :: Parsing response field of chain record {name}, field = {fields}."
        )

        #   check the check the chain record template
        #       there are three chain record templates (template #80, template #85 and template #32766)
        if ChainRecord17Chars.isValidChainRecord(fields):
            #   this is a chain record for 17 chars, so extract it
            chain_record = ChainRecord17Chars.parseChainRecord(fields)
        elif ChainRecord10Chars.isValidChainRecord(fields):
            #   this is a chain record for 10 chars, so extract it
            chain_record = ChainRecord10Chars.parseChainRecord(fields)
        elif ChainRecord32Chars.isValidChainRecord(fields):
            #   this is a chain record for 32 chars, so extract it
            chain_record = ChainRecord32Chars.parseChainRecord(fields)
        else:
            #   invalid chain record template
            #       so close this stream and set the result as not a chain record
            self._session.error(
                f"StreamingChain :: Cannot parse chain {name} because it is an invalid chain."
            )
            #   do nothing, done
            return

        self._chain_records.add_record(name, chain_record)

        #   store the display template
        with self._displayTemplateLock:
            if not self._displayTemplate:
                # this is a first time that parsing found display template properties on this chain record, so store it
                self._displayTemplate = chain_record.displayTemplate
            else:
                #   the display template on the chain record must be the same
                assert self._displayTemplate == chain_record.displayTemplate

        self._session.debug(
            f"StreamingChain :: "
            f"DONE - Parsing response field of chain record {name}, field = {fields}."
        )

        #   done, return chain record
        return chain_record

    def _update_chain_record(self, name, update):
        """ Update existing chain record """
        self._session.info(
            f"StreamingChain :: Updating response field of chain record {name}, update = {update}."
        )

        #   get the fields from response message
        fields = _get_fields_from_response(update)

        chain_record = self._chain_records.get_record(name)

        #   check this chain record are valid or not?
        if not chain_record:
            #   invalid chain record, so don't need to call an update
            #       skip it
            self._session.warning(
                f"StreamingChain :: Skipping to update an invalid chain record = {name}."
            )
            return

        #   update the chain record
        chain_record_update_info = chain_record.update(fields)

        assert chain_record_update_info is not None
        #   do update the constituents
        assert self._chainRecordNameToNumOffsetsFromRootChainRecordDict is not None
        assert name in self._chainRecordNameToNumOffsetsFromRootChainRecordDict
        offsetFromRootChainRecord = (
            self._chainRecordNameToNumOffsetsFromRootChainRecordDict[name]
        )
        for index, (
            oldConstituent,
            newConstituent,
        ) in chain_record_update_info.indexToOldAndNewConstituentTupleDict.items():
            # determine relative index from root of the chain to this chain record
            relativeIndex = offsetFromRootChainRecord + index

            # check if old/new constituent are not a empty, this mean it updated on this index
            if oldConstituent and newConstituent:
                #   this is an update constituent, so call update
                self._update_constituent(relativeIndex, oldConstituent, newConstituent)

            # check if old constituent is a empty and new constituent is not a sempty, this mean it add on this index
            elif not oldConstituent and newConstituent:
                #   this is an add constituent, so call add
                self._append_constituent(relativeIndex, newConstituent)

            # check if old constituent is not  aempty and new constituent is a empty, this mean it remove on this index
            elif oldConstituent and not newConstituent:
                #   this is an add constituent, so call remove
                self._remove_constituent(relativeIndex, oldConstituent)

        self._session.info(
            f"StreamingChain :: chain record update info = {chain_record_update_info}."
        )

    # warning CODE_ME if prev/next field are changed. It rarely those fields are changed.

    def _process_remaining_update_messages(self):
        """ This function is designed for processing the remaining update message due to wait for decode completed """
        self._session.info("StreamingChain :: Processing remaining update messages.")

        #   loop until all remaining update messages processed
        while True:

            #   try pop the update message from the list
            try:
                with self._remainingUpdateMessageListLock:
                    (streamName, updateMessage) = self._remainingUpdateMessageList.pop(
                        0
                    )
            except IndexError:
                #   no remaining update message, done
                break

            #   process remaining update message
            self._update_chain_record(streamName, updateMessage)

        #   done
        self._session.info(
            "StreamingChain :: DONE - Processing remaining update messages."
        )

    ###############################################################
    #   internal add/remove/update constituents in the chain record functions

    def _add_constituent(self, index, constituent):
        """ Add new constituent to the chain record """
        self._session.debug(
            f"StreamingChain.add_constituent(index = {index}, constituent = {constituent})"
        )
        assert 0 <= index <= len(self._constituentList)

        #   replace constituent from None
        with self._constituentListLock:
            assert self._constituentList[index]
            self._constituentList[index] = constituent

        self._dispatch_event(self._on_add, index, constituent)

    def _append_constituent(self, index, constituent):
        """
        Append new constituent to the chain record
        note that this function use when decode the chain record
        """
        self._session.debug(
            f"StreamingChain.append_constituent(index = {index}, constituent = {constituent})"
        )
        assert index == len(self._constituentList)

        #   append new constituent to the chain record
        with self._constituentListLock:
            self._constituentList.append(constituent)

        self._dispatch_event(self._on_add, index, constituent)

    def _remove_constituent(self, index, constituent):
        """ Remove the index in constituent to be None """
        self._session.debug(
            f"StreamingChain.remove_constituent(index = {index}, constituent = {constituent})"
        )
        assert 0 <= index < len(self._constituentList)

        #   do remove given index in the chain record
        with self._constituentListLock:
            assert self._constituentList[index]
            self._constituentList.pop(index)

        self._dispatch_event(self._on_remove, index, constituent)

    def _update_constituent(self, index, oldConstituent, newConstituent):
        """ Update the constituent in the chain record """
        self._session.debug(
            f"StreamingChain.update_constituent("
            f"index = {index}, oldConstituent = {oldConstituent}, newConstituent = {newConstituent})"
        )
        assert 0 <= index < len(self._constituentList)

        #   do update given constituent in the chain record
        with self._constituentListLock:
            self._constituentList[index] = newConstituent

        self._dispatch_event(self._on_update, index, oldConstituent, newConstituent)

    ###############################################################
    #   internal handle stream callback functions

    def _on_refresh_handler(self, stream, message):
        """ Streaming callback function on refresh """
        self._session.info(
            f"StreamingChain.on_refresh(stream = {stream.name}, message = {message})"
        )

        #   get chain record name
        chain_record_name = stream.name

        #   do process the refresh
        self._process_chain_record(stream.name, message)

        self._chain_records.refreshed(chain_record_name)

    def _on_update_handler(self, stream, update):
        """ Streaming callback function on update """
        self._session.info(
            f"StreamingChain.on_update(stream = {stream.name}, update = {update})"
        )

        #   check updating chain is ready to update
        #       Did it finish decode the chain record?
        if not self._is_complete_decoded.done():
            #   it's still decoding the chain record,
            #       the update will be occur after the chain decode completed
            #   store the postpone update message
            with self._remainingUpdateMessageListLock:
                self._remainingUpdateMessageList.append((stream.name, update))

            #   do nothing
            self._session.warning(
                "StreamingChain :: waiting to update because chain decode does not completed."
            )
            return

        #   process remaining update message due to waiting to decode finished
        self._process_remaining_update_messages()

        #   do process the update
        self._update_chain_record(stream.name, update)

    def _on_status_handler(self, stream, status):
        """ Streaming callback function on status """
        self._session.info(
            f"StreamingChain.on_status(stream = {stream.name}, status = {status})"
        )

        #   get chain record name
        chain_record_name = stream.name

        self._chain_records.set_status(chain_record_name, status)

    def _on_complete_handler(self, stream):
        """ Streaming callback function on complete """
        self._session.info(f"StreamingChain.on_complete(stream = {stream.name})")

    def _on_error_handler(self, stream, error):
        """ Streaming callback function on error """
        self._session.info(
            f"StreamingChain.on_error(stream = {stream.name}, error = {error})"
        )

        self._dispatch_event(self._on_error, stream.name, error)

    def _dispatch_event(self, callback, *args, **kwargs):
        if self.is_pause():
            self._events_cache.append([callback, args, kwargs])
            return

        try:
            callback and callback(self, *args, **kwargs)
        except Exception as e:
            self._session.error(
                f"{callback} user function on streaming chain {self._name} raised error {e}"
            )
