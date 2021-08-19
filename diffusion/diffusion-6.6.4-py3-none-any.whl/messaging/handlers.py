""" Messaging handlers. """

from typing import Callable

from diffusion import datatypes as dt
from diffusion.handlers import Handler
from diffusion.internal import utils


class RequestHandler(Handler):
    """ Handler for messaging requests. """

    def __init__(
        self,
        callback: Callable,
        request_type: dt.DataTypeArgument,
        response_type: dt.DataTypeArgument,
    ):
        self.request_type = dt.get(request_type)
        self.response_type = dt.get(response_type)
        self.callback = utils.coroutine(callback)

    async def handle(self, event: str = "request", **kwargs) -> dt.DataType:
        """ Execute the callback. """
        request: dt.DataType = kwargs.pop("request")
        if not isinstance(request, self.request_type):
            raise dt.IncompatibleDatatypeError(
                "Incompatible request data type: "
                f"required: {self.request_type.__name__}; submitted: {type(request).__name__}"
            )
        response = await self.callback(request.value, **kwargs)
        try:
            response = self.response_type(response)
        except dt.DataTypeError as ex:
            raise dt.IncompatibleDatatypeError from ex
        return response
