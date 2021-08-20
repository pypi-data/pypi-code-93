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


class ViewMetadata(object):
    """this class is designed to handle the request and response to query view metadata in search api"""

    #   endpoint information

    class ViewMetadataData(Endpoint.EndpointData):
        """this class is designed for storing and managing the response view metadata data

        The possible capability flags are:
            Searchable : the property supports searching in a Filter or Boost parameter
            Sortable : the property supports sorting in an OrderBy parameter
            Navigable : bucketed breakdowns can be requested for this property in a Navigators parameter
            Groupable : the property supports grouping using the GroupBy and GroupCount parameters
            Exact : the property supports exact-match searching in a Filter or Boost parameter
            Symbol : the property represents a symbol, and can be used in lookup's Scope parameter

         Response example
            {
                "Properties": {
                    "AdjustmentFactor": {
                            "Type": "String",
                            "Searchable": true,
                            "Sortable": true,
                            "Exact": true
                            },
                    "FairValueRIC": {
                            "Type": "String"
                            },
                    "InitialPricePerShare": {
                            "Type": "Double",
                            "Searchable": true
                            },
                    "SymbolHistoryScope": {
                            "Type": "Nested",
                            "Properties": {
                                "EndDate": {
                                        "Type": "Date",
                                        "Searchable": true,
                                        "Sortable": true
                                        },
                                "StartDate": {
                                        "Type": "Date",
                                        "Searchable": true,
                                        "Sortable": true
                                        },
                                "SymbolType": {
                                        "Type": "String",
                                        "Searchable": true
                                        },
                                "SymbolValue": {
                                        "Type": "String",
                                        "Searchable": true
                                        }
                            }
                    }
                }
            }
        """

        #   reponse data keyword
        _ResponsePropertiesName = "Properties"
        _ResponseTypeName = "Type"

        #       possible types
        #   nested
        _ResponseNestedTypeName = "Nested"

        #       flags
        _ResponseSearchableName = "Searchable"
        _ResponseSortableName = "Sortable"
        _ResponseNavigableName = "Navigable"
        _ResponseGroupableName = "Groupable"
        _ResponseExactName = "Exact"
        _ResponseSymbolName = "Symbol"
        _ResponseFlagNames = [
            _ResponseSearchableName,
            _ResponseSortableName,
            _ResponseNavigableName,
            _ResponseGroupableName,
            _ResponseExactName,
            _ResponseSymbolName,
        ]

        def __init__(self, raw):
            Endpoint.EndpointData.__init__(self, raw)

            #   dataframe of this view metadata reponse
            self._dataframe = self._convertMetadataReponseToDataframe(raw)

        #   helper function to recursive over the nested type
        @staticmethod
        def _convertPropertyAttributes(
            propertyAttributeToPropertyDictDict,
            propertyName,
            ancestorPropertyNameTupe,
            propertyAttributeDict,
        ):
            """   convert each property into a dictionary of property attribute to property dictionary """

            #   depth of this property
            thisPropertyDepth = 1

            #   determine this attribute name tuple
            attributeNameTupe = ancestorPropertyNameTupe[:] + (propertyName,)

            #   check the attribute type is nested or not?
            propertyAttributeType = propertyAttributeDict[
                ViewMetadata.ViewMetadataData._ResponseTypeName
            ]
            if (
                propertyAttributeType
                == ViewMetadata.ViewMetadataData._ResponseNestedTypeName
            ):
                #   this property is a nested type, recursive convert this property attribute
                #   extract properties of this nested type
                thisPropertiesOfNestedType = propertyAttributeDict[
                    ViewMetadata.ViewMetadataData._ResponsePropertiesName
                ]

                #   loop over all nested attributes and convert it
                for (
                    nestedPropertyName,
                    nestedPropertyAttributeDict,
                ) in thisPropertiesOfNestedType.items():
                    #   call convert recusivly for nested type
                    ViewMetadata.ViewMetadataData._convertPropertyAttributes(
                        propertyAttributeToPropertyDictDict,
                        nestedPropertyName,
                        attributeNameTupe,
                        nestedPropertyAttributeDict,
                    )

                #   increase property depth by one
                thisPropertyDepth += 1

            #   convert the attribute flags of this property attributes
            #       loop over all possible attributes and convert it
            for propertyAttributeName in [
                ViewMetadata.ViewMetadataData._ResponseTypeName,
            ] + ViewMetadata.ViewMetadataData._ResponseFlagNames:
                #   add properties of properties to dict of dict
                #       fill with None if the properties doesn't exist
                propertyDict = propertyAttributeToPropertyDictDict.setdefault(
                    propertyAttributeName, OrderedDict()
                )
                propertyDict[attributeNameTupe] = (
                    propertyAttributeDict[propertyAttributeName]
                    if propertyAttributeName in propertyAttributeDict
                    else False
                )
            #   done
            return thisPropertyDepth

        @staticmethod
        def _convertMetadataReponseToDataframe(raw):
            """ parse the metadata response from dict of dict to be a dict of dict tuple """

            #   convert the response to be welled structure as dict of dict

            #   get properties from raw response
            assert ViewMetadata.ViewMetadataData._ResponsePropertiesName in raw
            properties = raw[ViewMetadata.ViewMetadataData._ResponsePropertiesName]

            #   loop over view metadata and convert it to dict of dict tuple
            propertyAttributeToPropertyDictDict = {}
            propertyNameToDepthDict = {}
            for propertyName, propertyAttributeDict in properties.items():
                #   do convert each property attributes into dict of dict
                thisPropertyDepth = (
                    ViewMetadata.ViewMetadataData._convertPropertyAttributes(
                        propertyAttributeToPropertyDictDict,
                        propertyName,
                        (),
                        propertyAttributeDict,
                    )
                )

                #   store each property depth as dict
                propertyNameToDepthDict[propertyName] = thisPropertyDepth

            ######################################################
            #   convert response to be a dataframe format
            # warning OPTIMIZE_ME :: THIS CAN BE OPTIMIZE

            #   determine the maximum depth on nested property
            maxPropertyDepth = max(list(propertyNameToDepthDict.values()))

            #   loop over all the propertyAttributeToPropertyDictDict and convert to a dataframe format
            dataframe = {}
            for (
                propertyAttributeName,
                propertyDict,
            ) in propertyAttributeToPropertyDictDict.items():
                for propertyKey, propertyValue in propertyDict.items():
                    #   construct the property attribute for this property
                    dataframePropertyDict = dataframe.setdefault(
                        propertyAttributeName, OrderedDict()
                    )

                    #   construct the key of dataframe property
                    dataframePropertyKey = (
                        ViewMetadata.ViewMetadataData._extendTupleWithLastElement(
                            propertyKey, maxPropertyDepth
                        )
                    )
                    dataframePropertyDict[dataframePropertyKey] = propertyValue

            #   done, return dataframe
            if len(dataframe) == 0:
                return DataFrame([])
            else:
                return DataFrame(dataframe).convert_dtypes()

            #####################################################

        #   helper functionss

        @staticmethod
        def _extendTupleWithLastElement(inputTuple, numExpectedTupleElements):
            """ do extend the input tuple by duplicate last element value to be the expected number of tuple elements """
            numInputTupleElements = len(inputTuple)
            return inputTuple + inputTuple[numInputTupleElements - 1 :] * (
                numExpectedTupleElements - numInputTupleElements
            )

    def __init__(self, session, onResponseCallbackFunc=None):

        config = session._get_endpoint_config("discovery.search")
        base_url = config.get_str("url")
        metadata_url = config.get_str("endpoints.metadata")
        self._url = urljoin(base_url, metadata_url)

        #   session
        self._session = session

        #   callback functions
        #       on_response
        self._onResponseCallbackFunc = onResponseCallbackFunc

        #   endpoint information
        self._endpoint = None

        #   store the response from endpoint request
        self._response = None

    @property
    def response(self):
        return self._response

    ###########################################################
    #   callback function

    def _onResponse_cb(self, endpoint, response):
        """ callback when response occurred """

        #   do call the registered callback
        if self._onResponseCallbackFunc:
            #   the on response callback was registered, so call it
            # warning IMRPOVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC VIEW METADATA RESPONSE
            if response.is_success:
                #   success request, so parse the reponse into view metadata data
                response._data = ViewMetadata.ViewMetadataData(response.data.raw)
            self._onResponseCallbackFunc(endpoint, response)

    ###############################################################
    #   asynchronous methods

    async def _get_metadata_async(self, *, view):
        """this is a internal query view metadata function it require views."""
        from refinitiv.dataplatform.factory.delivery_factory import DeliveryFactory

        #   constructure the endpoint handler with given view
        self._endpoint = DeliveryFactory.create_end_point(
            self._session, urljoin(self._url, view.name), self._onResponse_cb
        )
        #   send the request asynchronously
        response = await self._endpoint.send_request_async(
            method=Endpoint.RequestMethod.GET,
        )

        #   store the response
        # warning IMRPOVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC VIEW METADATA RESPONSE
        self._response = response
        if self._response.is_success:
            #   success request, so parse the reponse into view metadata data
            self._response._data = ViewMetadata.ViewMetadataData(response.data.raw)

        #   done, return response
        return self.response

    @staticmethod
    async def get_metadata_async(*, session=None, on_response=None, view):
        """call asynchronous for getting view metadata

        Parameters
        ----------
        session: object
            the session for calling a lookup
        on_response: function, optional
            a callback function when response from lookup requested
            default: None
        view: object
            picks a subset of the data universe to search against. see SearchViews

        Returns
        -------
        object
            The response object from given view
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct view metadata object and call asynchronous view metadata method
        viewMetadata = ViewMetadata(session, onResponseCallbackFunc=on_response)
        response = await viewMetadata._get_metadata_async(view=view)

        #   done, return response
        return response

    ###############################################################
    #   synchronous methods

    @staticmethod
    def get_metadata(*, session=None, view):
        """call synchronous for getting view metadata

        Parameters
        ----------
        session: object
            the session for calling a lookup
        view: object
            picks a subset of the data universe to search against. see SearchViews

        Returns
        -------
        object
            The response object from given view
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct view metadata object and call asynchronous view metadata method
        viewMetadata = ViewMetadata(session)
        asyncio.get_event_loop().run_until_complete(
            viewMetadata._get_metadata_async(view=view)
        )

        #   done, return response
        return viewMetadata.response
