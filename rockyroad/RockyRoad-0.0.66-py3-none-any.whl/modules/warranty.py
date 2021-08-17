from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Warranties(Consumer):
    """Inteface to Warranties resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def creditRequests(self):
        return self.__Credit_Requests(self)

    def rates(self):
        return self.__Rates(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Credit_Requests(Consumer):
        """Inteface to Warranties Credit Requests resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        def messages(self):
            return self.__Messages(self)

        @returns.json
        @get("warranties/credit-requests")
        def list(
            self,
            uid: Query(type=str) = None,
            claimReference: Query(type=str) = None,
        ):
            """This call will return detailed warranty credit request information for the specified criteria."""

        @returns.json
        @delete("warranties/credit-requests")
        def delete(self, uid: Query(type=str)):
            """This call will delete the warranty credit request for the specified uid."""

        @returns.json
        @json
        @post("warranties/credit-requests")
        def insert(self, creditRequest: Body):
            """This call will create a warranty credit request with the specified parameters."""

        @returns.json
        @json
        @patch("warranties/credit-requests")
        def update(self, creditRequest: Body):
            """This call will update the warranty credit request with the specified parameters."""

        @returns.json
        @multipart
        @post("warranties/credit-requests/add-files")
        def addFile(self, uid: Query(type=str), file: Part):
            """This call will a upload file for a warranty credit request with the specified uid."""

        @get("warranties/credit-requests/download-files")
        def downloadFile(
            self,
            uid: Query(type=str),
            filename: Query(type=str),
        ):
            """This call will download the file associated with the warranty credit request with the specified uid."""

        @returns.json
        @get("warranties/credit-requests/list-files")
        def listFiles(
            self,
            uid: Query(type=str),
        ):
            """This call will return a list of the files associated with the warranty credit request for the specified uid."""

        @headers({"Ocp-Apim-Subscription-Key": key})
        class __Messages(Consumer):
            """Inteface to Warranties Credit Requests Messages resource for the RockyRoad API."""

            def __init__(self, Resource, *args, **kw):
                super().__init__(base_url=Resource._base_url, *args, **kw)

            @returns.json
            @get("warranties/credit-requests/messages")
            def list(
                self,
                warranty_credit_request_uid: Query(type=str),
            ):
                """This call will return detailed warranty credit request message information for the specified criteria."""

            @returns.json
            @delete("warranties/credit-requests/messages")
            def delete(self, uid: Query(type=str)):
                """This call will delete the warranty credit request message for the specified uid."""

            @returns.json
            @json
            @post("warranties/credit-requests/messages")
            def insert(self, message: Body):
                """This call will create a warranty credit request with the specified parameters."""

            @returns.json
            @json
            @patch("warranties/credit-requests/messages")
            def update(self, message: Body):
                """This call will update the warranty credit request with the specified parameters."""

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Rates(Consumer):
        """Inteface to Warranties Rates resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            self._base_url = Resource._base_url
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("warranties/rates")
        def list(
            self,
            uid: Query(type=str) = None,
            dealer_account: Query(type=str) = None,
            daaler_account_uid: Query(type=str) = None,
        ):
            """This call will return detailed waranty rate information for the specified criteria."""

        @returns.json
        @delete("warranties/rates")
        def delete(self, uid: Query(type=str)):
            """This call will delete the warranty rates for the specified uid."""

        @returns.json
        @json
        @post("warranties/rates")
        def insert(self, warrantyRates: Body):
            """This call will create warranty rates with the specified parameters."""

        @returns.json
        @json
        @patch("warranties/rates")
        def update(self, warrantyRates: Body):
            """This call will update the warranty rates with the specified parameters."""