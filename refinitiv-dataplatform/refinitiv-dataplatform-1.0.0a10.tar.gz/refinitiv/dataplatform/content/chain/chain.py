# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import asyncio

from pandas import DataFrame

###############################################################
#
#   REFINITIV IMPORTS
#

from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.tools._common import urljoin


###############################################################
#
#   LOCAL IMPORTS
#

###############################################################
#
#   CLASSES
#


class Chain(object):
    """ this class is designed to handle the request and response for chian Refinitiv data platform api """

    class Data(Endpoint.EndpointData):
        """this class is designed for storing and managing the response chain constituent data

        response structure
            chain response
            {
                "universe": {
                    "displayName : str,
                    "ric": str
                },
                "data": {
                    "consituents : [str]
                }
            }

        response example
        {
            "universe": {
                "ric": ".AV.O",
                "displayName": "TOP 25 BY VOLUME",
                "serviceName": "ELEKTRON_DD"
            },
            "data": {
                "constituents": ["QQQ.O", "AMD.O", "AAPL.O", "INO.O", "MSFT.O",
                                 "AYTU.O", "SQQQ.O", "TQQQ.O", "CMCSA.O", "AAL.O",
                                 "CSCO.O", "INTC.O", "FB.O", "CZR.O", "SIRI.O",
                                 "MU.O", "JD.O", "GILD.O", "CODX.O", "OAS.O",
                                 "SBUX.O", "TBLT.O", "TLT.O", "ZNGA.O", "FCEL.O"]
            }
        }
        """

        #   response universe keyword
        _response_universe_name = "universe"
        _response_ric_name = "ric"
        _response_display_name_name = "displayName"
        _response_service_name_name = "serviceName"

        #   response data keyword
        _response_data_name = "data"
        _response_constitients_name = "constituents"

        def __init__(self, raw):
            Endpoint.EndpointData.__init__(self, raw)
            #   convert raw data to dataframe data format
            #       dataframe is a dictionary of list data
            #   key of dictionary will be a header of the field
            self._dataframe = self._convert_raw_to_dataframe(raw)

        @staticmethod
        def _convert_raw_to_dataframe(raw):
            """ convert the raw response chain to dataframe format """

            #######################################
            #   chain information
            assert Chain.Data._response_universe_name in raw

            #   extract universe
            universe = raw[Chain.Data._response_universe_name]
            assert Chain.Data._response_ric_name in universe

            #   extract ric
            ric = universe[Chain.Data._response_ric_name]

            #######################################
            #   constituents
            assert Chain.Data._response_data_name in raw

            #   extract the data from response
            data = raw[Chain.Data._response_data_name]
            assert Chain.Data._response_constitients_name in data

            #   extract constituents from data
            constituents = data[Chain.Data._response_constitients_name]

            #   construct pandas dataframe from constituents
            _df = None
            if len(constituents):
                _df = DataFrame({ric: constituents})
            else:
                _df = DataFrame([], columns=[ric])
            if not _df.empty:
                _df = _df.convert_dtypes()
            return _df

    def __init__(self, session, on_response=None):
        from refinitiv.dataplatform.factory.delivery_factory import DeliveryFactory

        config = session._get_endpoint_config("data.pricing")
        base_url = config.get_str("url")
        chains_url = config.get_str("endpoints.chains")
        _url = urljoin(base_url, chains_url) + "?universe={universe}"

        #   session
        self._session = session

        #   callback functions
        #       on_response
        self._on_response_cb_func = on_response

        #   endpoint information
        self._endpoint = DeliveryFactory.create_end_point(
            self._session, _url, on_response=self._on_response_cb
        )

        #   store the response from endpoint request
        self._response = None

    @property
    def response(self):
        return self._response

    ###########################################################
    #   callback legacy

    def _on_response_cb(self, endpoint, response):
        """ callback when response occurred """

        #   do call the registered callback
        if self._on_response_cb_func:
            #   the on response callback was registered, so call it
            if response.is_success:
                #   success request, so parse the response into chain constituents data
                # warning IMPROVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC CHAIN RESPONSE DATA
                response._data = self.Data(response.data.raw)
            self._on_response_cb_func(endpoint, response)

    ###############################################################
    #   asynchronous methods

    async def _decode_async(self, *, universe, **kwargs):
        """ this is a internal chain decoding legacy it require universe as chain record name """

        #   send the request asynchronously
        response = await self._endpoint.send_request_async(
            method=Endpoint.RequestMethod.GET,
            header_parameters={"Content-Type": "application/json"},
            path_parameters={"universe": universe},
        )

        #   store response
        self._response = response
        #   parse the response
        if self._response.is_success:
            #   success request, so parse the response into chain constituents data
            # warning IMPROVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC CHAIN RESPONSE DATA
            self._response._data = self.Data(response.data.raw)

        #  done, return response
        return self._response

    @staticmethod
    async def decode_async(*, session=None, on_response=None, universe, **kwargs):
        """Call synchronous a decode chain with given universe parameter

        Parameters
        ----------
        session: object
            The session for calling a decoding chain
        on_response: legacy, optional
            A callback legacy when response from decoding chain requested, default: None
        universe: str
            The chain record name to decode ie. 0#.DJI or .AV.O

        Returns
        -------
        EndpointResponse
            The response object from given chain parameters
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct chain object and call asynchronous chain decoding method
        chain = Chain(session, on_response=on_response)
        response = await chain._decode_async(universe=universe, **kwargs)

        #   done, return response
        return response

    ###############################################################
    #   synchronous methods

    @staticmethod
    def decode(*, session=None, on_response=None, universe, **kwargs):
        """Call synchronous a decode chain with given universe parameter

        Parameters
        ----------
        session: object, optional
            The session for calling a decoding chain, default: default session
        on_response: legacy, optional
            A callback legacy when response from decoding chain requested, default: None
        universe: str
            The chain record name to decode ie. 0#.DJI or .AV.O

        Returns
        -------
        EndpointResponse
            The response object from given chain name parameters
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct chain object and call asynchronous chain decoding method
        chain = Chain(session, on_response=on_response)
        asyncio.get_event_loop().run_until_complete(
            chain._decode_async(universe=universe, **kwargs)
        )

        #   done, return response
        return chain.response
