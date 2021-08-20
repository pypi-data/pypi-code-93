from refinitiv.dataplatform.delivery.data import Endpoint

from .data import ESGData


def _parse_error(error):
    error_code = error.get("code")
    error_message = error.get("description")
    if not error_message:
        error_message = error.get("message")
        errors = error.get("errors")
        if isinstance(errors, list):
            error_message += ":\n"
            error_message += "\n".join(map(str, errors))

    return error_code, error_message


class ESGResponse(Endpoint.EndpointResponse):
    def __init__(self, response, convert_function):
        super().__init__(response)
        if self.is_success:

            raw_data = self._data.raw

            error = raw_data.get("error", False)
            if error:
                self._error_code, self._error_message = _parse_error(error)
                self._is_success = False
            else:
                self._data = ESGData(raw_data, convert_function(raw_data))
        else:
            content = self._status.get("content", False)
            if content and "error" in content:
                error = content["error"]
                self._error_code, self._error_message = _parse_error(error)
