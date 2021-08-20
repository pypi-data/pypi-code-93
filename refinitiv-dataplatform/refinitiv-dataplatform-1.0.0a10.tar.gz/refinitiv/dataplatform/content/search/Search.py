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
from refinitiv.dataplatform.tools._common import urljoin
from refinitiv.dataplatform.delivery.data import Endpoint


###############################################################
#
#   LOCAL IMPORTS
#
from .SearchViews import SearchViews

###############################################################
#
#   CLASSES
#


class Search(object):
    """ this class is designed to handle the request and response for search api """

    #   endpoint information
    #   endpoint request body keyword parameter names (require fields)
    #       view
    _EndPointViewParameterName = "View"

    #   mapping between python keyword argument to api paramenter name
    _PythonKeywordArgumentNameToEndPointParameterName = {
        "boost": "Boost",
        "features": "Features",
        "filter": "Filter",
        "group_by": "GroupBy",
        "group_count": "GroupCount",
        "navigators": "Navigators",
        "order_by": "OrderBy",
        "query": "Query",
        "scope": "Scope",
        "select": "Select",
        "skip": "Skip",
        "terms": "Terms",
        "top": "Top",
        "view": "View",
    }

    class SearchData(Endpoint.EndpointData):
        """this class is designed for storing and managing the response search data

         response structure
             search response
             {
                 DidYiuMean : string,
                 Hits : array of object,
                 Navigators : see search response navigator structure,
                 Skipped : integer,
                 Total : integer,
                 Warnings : array of string,
             }

             search response navigator
             {
                 description : { Bucket : array of [ Count : integer,
                                                     Filter : string,
                                                     Label : string,
                                                     < * > : sub-navigator
                                                 ]
                             }
             }

        response example
        {
            "Total": 82,
            "Hits": [
                {
                    "FirstName": "Othmar",
                    "LastName": "Dubach",
                    "AllRoles": [
                            "Officer and Director"
                    ]
                },
                {
                    "FirstName": "Barry",
                    "LastName": "Irvin",
                    "MiddleName": "Andrew",
                    "AllRoles": [
                            "Officer and Director"
                    ]
                }
            ]
        }

        response with navigator example
        {
            "Total": 523876,
            "Hits": [],
            "Navigators": {
                "Eps": {
                "Buckets": [
                        {
                            "Label": "0",
                            "Filter": "(Eps ge 0 and Eps lt 5)",
                            "Count": 448547
                        },
                        {
                            "Label": "5",
                            "Filter": "(Eps ge 5 and Eps lt 10)",
                            "Count": 47235
                        },
                        {
                            "Label": "10",
                            "Filter": "(Eps ge 10 and Eps lt 15)",
                            "Count": 18149
                        },
                        {
                            "Label": "15",
                            "Filter": "Eps ge 15",
                            "Count": 9945
                        }
                    ]
                }
            }
        }

        response with sub-navigator example
        {
            "Total": 2289306,
            "Hits": [],
            "Navigators": {
                "FirstName": {
                "Buckets": [
                        {
                            "Label": "John",
                            "Count": 35934,
                            "LastName": {
                                "Buckets": [
                                    {
                                        "Label": "Anderson",
                                        "Count": 96
                                    }
                                ]
                            }
                        },
                        {
                            "Label": "David",
                            "Count": 34038,
                            "LastName": {
                                "Buckets": [
                                    {
                                        "Label": "Smith",
                                        "Count": 211
                                    }
                                ]
                            }
                        },
                        {
                            "Label": "Michael",
                            "Count": 32583,
                            "LastName": {
                                "Buckets": [
                                    {
                                        "Label": "Smith",
                                        "Count": 150
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        }
        """

        #   reponse data keyword
        _ResponseWarningsName = "Warnings"
        _ResponseTotalName = "Total"
        _ResponseHitsName = "Hits"
        _ResponseNavigatorName = "Navigators"
        _ResponseDidYouMeanName = "DidYouMean"

        #       navigator and sub-navigator
        _ResponseNavigatorLableName = "Label"
        _ResponseNavigatorCountName = "Count"
        _ResponseNavigatorBucketsName = "Buckets"
        _ResponseNavigatorFilterName = "Filter"

        def __init__(self, raw):
            Endpoint.EndpointData.__init__(self, raw)
            #   convert raw data to dataframe data format
            #       dataframe is a dictionary of list data
            #   key of dictionary will be a header of the field
            self._dataframe, self._navigatorDataframeDict = self._convertRawToDataframe(
                raw
            )

            #   get the number of total hits
            assert self._ResponseTotalName in raw
            self._total = raw[self._ResponseTotalName]

        @property
        def total(self):
            return self._total

        # warning IMPROVE_ME :: NEED A BETTER UNDERSTANDING NAVIGATOR
        # warning UNCOMMENT_ME :: TO ENABLE NAVIGATOR
        # @property
        # def navigators( self ):
        #     return self._navigatorDataframeDict

        @staticmethod
        def _convertRawToDataframe(raw):
            """ convert the raw response search to dataframe format """

            #######################################
            #   hits

            assert Search.SearchData._ResponseHitsName in raw
            hits = raw[Search.SearchData._ResponseHitsName]

            #   convert hits from list of dictionary to dictionary of list
            hitDataframe = Search.SearchData._convertListOfDictToDictOfList(hits)

            #######################################
            #   navigator

            #   check for a navigator response (optinal response)
            navigatorDataframeDict = {}
            # warning IMPROVE_ME :: NEED A BETTER UNDERSTANDING NAVIGATOR
            # warning UNCOMMENT_ME :: TO ENABLE NAVIGATOR
            # if Search.SearchData._ResponseNavigatorName in raw :
            #     #   get navigators from response
            #     navigators = raw[ Search.SearchData._ResponseNavigatorName ]

            #     #   loop over all navigate results and do convert to dataframe
            #     for navigatorName, navigatorValues in navigators.items():

            #         #   loop over all items in bucket and convert each navigate result to dataframe
            #         navigatorDataframe = {}
            #         bucketItems = navigatorValues[ Search.SearchData._ResponseNavigatorBucketsName ]
            #         for bucketItem in bucketItems:
            #             Search.SearchData._convertNavigatorToDataframe( navigatorDataframe, navigatorName, bucketItem )

            #         #   store each navigate result in dataframe
            #         navigatorDataframeDict[navigatorName] = navigatorDataframe

            #  done, return
            # return ( hitDataframe, navigatorDataframeDict, )

            if hitDataframe:
                _data_frame = DataFrame(hitDataframe)
                if not _data_frame.empty:
                    _data_frame = _data_frame.convert_dtypes()
                return (
                    _data_frame,
                    navigatorDataframeDict,
                )
            else:
                return (DataFrame([]), navigatorDataframeDict)

        @staticmethod
        def _convertNavigatorToDataframe(
            dataframe, navigatorName, bucketItem, ancestorNavigatorNameToLabelDict={}
        ):
            """ do a convert from navigator to dataframe """

            #   this is a all key in this bucket item
            #       the remaining key is used for determine the sub-navigate
            remainingBucketItemKeys = list(bucketItem.keys())

            #  extract the label, count and filter if it exists

            #   extract lable form bucket item
            #       and remove the label from remaining bucket item keu
            assert Search.SearchData._ResponseNavigatorLableName in bucketItem
            label = bucketItem[Search.SearchData._ResponseNavigatorLableName]
            remainingBucketItemKeys.remove(
                Search.SearchData._ResponseNavigatorLableName
            )

            #   count
            assert Search.SearchData._ResponseNavigatorCountName in bucketItem
            count = bucketItem[Search.SearchData._ResponseNavigatorCountName]
            remainingBucketItemKeys.remove(
                Search.SearchData._ResponseNavigatorCountName
            )

            #   store this navigate result in the dataframe
            navigatorLabelList = dataframe.setdefault(navigatorName, [])
            navigatorLabelList.append(label)
            navigatorCountList = dataframe.setdefault(
                Search.SearchData._ResponseNavigatorCountName, []
            )
            navigatorCountList.append(count)

            #   add the ancestor data into dataframe for sub-navigate
            for (
                ancestorNavigatorName,
                ancestorNavigatorLabel,
            ) in ancestorNavigatorNameToLabelDict.items():
                ancestorNavigatorList = dataframe[ancestorNavigatorName]
                ancestorNavigatorList.append(ancestorNavigatorLabel)

            #   loop the remaining bucket item key
            for bucketItemKey in remainingBucketItemKeys:

                #   extract value of this key
                bucketItemValue = bucketItem[bucketItemKey]
                if type(bucketItemValue) is not dict:
                    #   this is a item property.
                    #   store this navigate result in the dataframe
                    dataframeItemVals = dataframe.setdefault(bucketItemKey, [])
                    dataframeItemVals.append(bucketItemValue)

                else:
                    #   this is a sub-navigator

                    #   this item has sub-navigator, so extract it
                    subNavigatorName = remainingBucketItemKeys[0]
                    subNavigatorValues = bucketItem[subNavigatorName]

                    #   add the ancestor navigate name and label
                    ancestorNavigatorNameToLabelDict = (
                        ancestorNavigatorNameToLabelDict.copy()
                    )
                    ancestorNavigatorNameToLabelDict[navigatorName] = label

                    #   get list of all bucket items in this sub-navigators
                    subNavigatorBucketItems = subNavigatorValues[
                        Search.SearchData._ResponseNavigatorBucketsName
                    ]

                    #   check bucket item exist or not?
                    if len(subNavigatorBucketItems) > 0:
                        #   need to add the dataframe for this sub-navigate
                        navigatorList = dataframe.setdefault(subNavigatorName, [])
                        navigatorList.append(None)

                    #   do loop over all bucket items in sub-navigate
                    #       and recursivly call the convert to dataframe
                    for subNavigatorBucketItem in subNavigatorBucketItems:
                        #   call convert this sub-navigate to dataframe
                        Search.SearchData._convertNavigatorToDataframe(
                            dataframe,
                            subNavigatorName,
                            subNavigatorBucketItem,
                            ancestorNavigatorNameToLabelDict,
                        )

        @staticmethod
        def _convertListOfDictToDictOfList(listOfDict):
            """do convert from list of dictionary to dictionary to list with fill non-exists key by None
            ie. from [ { 'a' : 1, 'b' : 2 }, { 'a' : 11, 'b' : 22 } ]
                to { 'a' : [ 1, 2 ], 'b' : [ 2, 22 ] }
            """

            #   convert from list of dictionary to dictionary of list
            # warning IMPROVE_ME :: DO OPTIMIZE HERE
            #   list all all possible keys
            keys = set(
                [
                    key
                    for keys in [list(item.keys()) for item in listOfDict]
                    for key in keys
                ]
            )

            #   convert the hits from list of dict to dict of list
            #       insert the non-exist key to None
            return {
                key: [item[key] if key in item else None for item in listOfDict]
                for key in keys
            }

    def __init__(self, session, onResponseCallbackFunc=None):
        from refinitiv.dataplatform.factory.delivery_factory import DeliveryFactory

        config = session._get_endpoint_config("discovery.search")
        base_url = config.get_str("url")
        search_url = config.get_str("endpoints.search")
        _url = urljoin(base_url, search_url)

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
        if self._onResponseCallbackFunc:
            #   the on response callback was registered, so call it
            # warning IMPROVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC SEARCH RESPONSE
            if response.is_success:
                #   success request, so parse the reponse into search data
                response._data = Search.SearchData(response.data.raw)
            self._onResponseCallbackFunc(endpoint, response)

    ###############################################################
    #   helper methods

    def _constuctBodyParameters(self, view, kwargs):
        """convert the python keyword arguments to the body parameters

        Returns
        -------
        dictionary
            The body parameters of a request. It's a mapping between API parameter name to value.

        Raises
        ------
        ValueError
            If given an invalid keyword argument.
        """

        #   convert keyword args to the API parameter name
        parameters = {}
        for name, value in kwargs.items():
            #   do convert the python keyword args to API parameter name
            if name not in self._PythonKeywordArgumentNameToEndPointParameterName:
                #   invalid keyword args, so raise ValueError
                raise ValueError('Error!!! Invalid argument "{}" name.'.format(name))

            #   convert and store in parameter dict
            parameterName = self._PythonKeywordArgumentNameToEndPointParameterName[name]
            parameters[parameterName] = value

        #   add the view this is a special because this is a require field
        parameters[self._EndPointViewParameterName] = view.value

        #   done, return the mapping between between API parameter name to value.
        return parameters

    ###############################################################
    #   asynchronous methods

    async def _search_async(self, query=None, *, view=SearchViews.SearchAll, **kwargs):
        """this is a internal search legacy it require search views,
            and keyword arguments that relate to the given view.
        (use search lookup to see the possible arguments for each view)
        """

        #   construct the body data for a request
        #       parameters including view (required) and other optional arguments
        bodyParameters = self._constuctBodyParameters(view, kwargs)

        if query:
            bodyParameters["Query"] = query

        #   send the request asynchronously
        response = await self._endpoint.send_request_async(
            method=Endpoint.RequestMethod.POST,
            header_parameters={"Content-Type": "application/json"},
            body_parameters=bodyParameters,
        )

        #   store the response
        # warning IMPROVE_ME :: THIS IS A WORKAROUND FOR CONVERT GENERAL ENDPOINT RESPONSE TO THIS SPECIFIC SEARCH RESPONSE
        self._response = response
        if self._response.is_success:
            #   success request, so parse the reponse into search data
            self._response._data = Search.SearchData(response.data.raw)

        #   done, return response
        return self.response

    @staticmethod
    async def search_async(
        *, session=None, on_response=None, view=SearchViews.SearchAll, **kwargs
    ):
        """call asynchronous search with given view and search parameters

        Parameters
        ----------
        session: object
            the session for calling a search
        on_response: legacy, optional
            a callback legacy when response from search requested
            default: None
        view: object
            the view for searching see at SearchViews object
        kwargs: dict
            this is a keyword arguments related to each view

        Returns
        -------
        object
            The response object from given search parameters
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct search object and call asynchronous search method
        search = Search(session, onResponseCallbackFunc=on_response)
        response = await search._search_async(view=view, **kwargs)

        #   done, return response
        return response

    ###############################################################
    #   synchronous methods

    @staticmethod
    def search(query=None, *, session=None, view=SearchViews.SearchAll, **kwargs):
        """call synchronous search with given view and search parameters

        Parameters
        ----------
        session: object, optional
            the session for calling a search
            default: default session
        query: string
            optional keyword argument for view
        view: object
            the view for searching see at SearchViews object
        kwargs: dict
            this is a keyword arguments related to each view

        Returns
        -------
        object
            The response object from given search parameters
        """
        #   check for using default session
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session if session else DefaultSession.get_default_session()

        #   construct search object and call asynchronous search method
        search = Search(session)
        asyncio.get_event_loop().run_until_complete(
            search._search_async(query=query, view=view, **kwargs)
        )

        #   done, return response
        return search.response
