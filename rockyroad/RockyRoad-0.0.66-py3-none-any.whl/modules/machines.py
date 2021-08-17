from .module_imports import *


@headers({"Ocp-Apim-Subscription-Key": key})
class Machines(Consumer):
    """Inteface to machine resource for the RockyRoad API."""

    def __init__(self, Resource, *args, **kw):
        self._base_url = Resource._base_url
        super().__init__(base_url=Resource._base_url, *args, **kw)

    def serials(self):
        return self.__Serials(self)

    @headers({"Ocp-Apim-Subscription-Key": key})
    class __Serials(Consumer):
        """Inteface to machine serial resource for the RockyRoad API."""

        def __init__(self, Resource, *args, **kw):
            super().__init__(base_url=Resource._base_url, *args, **kw)

        @returns.json
        @get("machines/models/serials")
        def list(
            self,
            model: Query(type=str) = None,
            brand: Query(type=str) = None,
        ):
            """This call will machine serials for the specified criteria."""
