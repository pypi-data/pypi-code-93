# coding: utf-8

###############################################################
#
#   STANDARD IMPORTS
#

import asyncio

from collections import OrderedDict

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


class Lookup(object):
    """ this class is designed to handle the request and response for lookup in search api """

    #   endpoint information
    #   endpoint request body keyword parameter names (require field)
    #       view
    _EndPointViewParameterName = "View"
    #       terms
    _EndPointTermsParameterName = "Terms"
    #       scope
    _EndPointScopeParameterName = "Scope"
    #       select
    _EndPointSelectParameterName = "Select"

    #   optional
    #       filter
    _EndPointFilterParameterName = "Filter"
    #       boost
    _EndPointBoostParameterName = "Boost"

    class LookupData(Endpoint.EndpointData):
        """this class is designed for storing and managing the response lookup data

        Response example
        I.
        {
            "Matches": {
                    "A": {
                        "DocumentTitle": "Agilent Technologies Inc, Ordinary Share, MiFID Eligible Security, NYSE Consolidated",
                        "ExchangeCountry": "USA"
                        },
                    "B": {
                        "DocumentTitle": "Barnes Group Inc, Ordinary Share, MiFID Eligible Security, NYSE Consolidated",
                        "ExchangeCountry": "USA"
                        },
                    "C": {
                        "DocumentTitle": "Citigroup Inc, Ordinary Share, MiFID Eligible Security, NYSE Consolidated",
                        "ExchangeCountry": "USA"
                        }
                }
        }

        II.
        {
            "Matches": {
                        "B": {
                            "DocumentTitle": "This one worked fine",
                            "ExchangeCountry": "USA"
                            }
            },
            "FailedSubRequests": {
                        "A": "(timed out)"
            }
        }

        """

        #   reponse keyword name
        _ResponseMatchesName = "Matches"
        _ReponseFailedSubRequestsName = "FailedSubRequests"
        _ReponseWarningsName = "Warnings"

        def __init__(self, raw):
            Endpoint.EndpointData.__init__(self, raw)

            #   convert raw data to dataframe and index
            self._dataframe = self._convertLookupResponseToDataframe(raw)

        @staticmethod
        def _convertLookupResponseToDataframe(raw):
            """ convert a lookup response to the dataframe format """
            assert Lookup.LookupData._ResponseMatchesName in raw
            matches = raw[Lookup.LookupData._ResponseMatchesName]

            ###########################################################
            #       matches
            #   loop over all matches and construct the dataframe format
            matchDataframe = {}
            #   list all all possible property names
            matchesListOfDict = [matches[key] for key in matches.keys()]
            propertyNames = set(
                [
                    key
                    for keys in [list(item.keys()) for item in matchesListOfDict]
                    for key in keys
                ]
            )
            for matchName, matchValueDict in matches.items():
                #   loop over all properties in mached
                #       and convert each match to dataframe
                # for matchPropertyName, matchPropertyValue in matchValueDict.items():
                for propertyName in propertyNames:
                    #   create or append properties value to dict of each row
                    matchPropertyDataframeDict = matchDataframe.setdefault(
                        propertyName, OrderedDict()
                    )
                    matchPropertyDataframeDict[matchName] = (
                        matchValueDict[propertyName]
                        if propertyName in matchValueDict
                        else None
                    )

            #   done, return
            if matchDataframe:
                df = DataFrame(matchDataframe)
                if not df.empty:
                    return df.convert_dtypes()
                return df
            return DataFrame([])

    def __init__(self, session, onResponseCallbackFunc=None):
        from refinitiv.dataplatform.factory.delivery_factory import DeliveryFactory

        config = session._get_endpoint_config("discovery.search")
        base_url = config.get_str("url")
        lookup_url = config.get_str("endpoints.lookup")
        _url = urljoin(base_url, lookup_url)

        #   session
        self._session = session

        #   callback functions
        #       on_response
        self._onResponseCallbackFunc = onResponseCallbackFunc

        #   endpoint information
        self._endpoint = DeliveryFactory.create_end_point(
            self._session, _url, self._onResponse_cb
        )

        #   store the response from endpoint request
        self._response = None

    @property
    def response(self):
        return self._response

    ###########################################################
    #   callback legacy

    def _onResponse_cb(self, endpoint, response):
        """ callback when response occurred """

        #   do call the registered callback
        self._response = response

        if self._onResponseCallbackFunc:
            #   the on response callback was registered, so call it
            # warning IMRPOVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC LOOKUP RESPONSE
            if response.is_success:
                #   success request, so parse the reponse into lookup data
                response._data = Lookup.LookupData(response.data.raw)
            self._onResponseCallbackFunc(endpoint, response)

    ###############################################################
    #   helper methods

    def _constuctBodyParameters(
        self, view, terms, scope, select, filter=None, boost=None
    ):
        """convert the python keyword arguments to the body parameters

        Returns
        -------
        dictionary
            The body parameters of a request. It's a mapping between API parameter name to value.

        """

        #   add the view this is a special because this is a require field
        parameters = {}
        parameters[self._EndPointViewParameterName] = view.value
        #       terms
        parameters[self._EndPointTermsParameterName] = terms
        #       scope
        parameters[self._EndPointScopeParameterName] = scope
        #       select
        parameters[self._EndPointSelectParameterName] = select

        #   optional
        #       filter
        if filter:
            parameters[self._EndPointFilterParameterName] = filter
        #       boost
        if boost:
            parameters[self._EndPointBoostParameterName] = boost

        #   done, return the mapping between between API parameter name to value.
        return parameters

    ###############################################################
    #   asynchronous methods

    async def _lookup_async(
        self, *, view, terms, scope, select, filter=None, boost=None, closure=None
    ):
        """this is a internal lookup legacy it require views, terms, scope and select.
        and keyword arguments are filter and boost.
        """

        #   construct the body data for a request
        #       parameters including view, terms, scope, select (required) and other optional arguments
        bodyParameters = self._constuctBodyParameters(
            view, terms, scope, select, filter, boost
        )

        #   send the request asynchronously
        response = await self._endpoint.send_request_async(
            method=Endpoint.RequestMethod.POST,
            header_parameters={"Content-Type": "application/json"},
            body_parameters=bodyParameters,
            closure=closure,
        )

        #   store the response
        # warning IMRPOVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC LOOKUP RESPONSE
        self._response = response
        if self._response.is_success:
            #   success request, so parse the reponse into lookup data
            self._response._data = Lookup.LookupData(response.data.raw)

        #   done, return response
        return self.response

    @staticmethod
    async def lookup_async(
        *,
        session=None,
        on_response=None,
        view,
        terms,
        scope,
        select,
        filter=None,
        boost=None,
        closure=None,
    ):
        """call asynchronous lookup with parameters

        Parameters
        ----------
        session: object
            the session for calling a lookup
        on_response: legacy, optional
            a callback legacy when response from lookup requested
            default: None
        view: object
            picks a subset of the data universe to search against. see SearchViews
        terms: string
            lists the symbols to be solved
        scope: string
            identifies the symbology which 'terms' belong to
        select: string
            specifies which properties to return for each result doc
        filter: string
            supports structured predicate expressions
        boost: string
            pushes documents matching a filter expression to the top of the list

        Returns
        -------
        object
            The response object from given lookup parameters
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct lookup object and call asynchronous lookup method
        lookup = Lookup(session, onResponseCallbackFunc=on_response)
        response = await lookup._lookup_async(
            view=view,
            terms=terms,
            scope=scope,
            select=select,
            filter=filter,
            boost=boost,
            closure=closure,
        )

        #   done, return response
        return response

    ###############################################################
    #   synchronous methods

    @staticmethod
    def lookup(*, session=None, view, terms, scope, select, filter=None, boost=None):
        """call synchronous lookup with given parameters

        Parameters
        ----------
        session: object
            the session for calling a lookup
        view: object
            picks a subset of the data universe to search against. see SearchViews
        terms: string
            lists the symbols to be solved
        scope: string
            identifies the symbology which 'terms' belong to
        select: string
            specifies which properties to return for each result doc
        filter: string
            supports structured predicate expressions
        boost: string
            pushes documents matching a filter expression to the top of the list

        Returns
        -------
        object
            The response object from given lookup parameters
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct lookup object and call asynchronous lookup method
        lookup = Lookup(session)
        asyncio.get_event_loop().run_until_complete(
            lookup._lookup_async(
                view=view,
                terms=terms,
                scope=scope,
                select=select,
                filter=filter,
                boost=boost,
            )
        )

        #   done, return response
        return lookup.response
