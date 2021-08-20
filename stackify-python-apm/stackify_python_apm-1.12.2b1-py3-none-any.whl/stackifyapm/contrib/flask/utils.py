from stackifyapm.conf import constants
from stackifyapm.utils import compat, get_url_data
from stackifyapm.utils.wsgi import get_headers


def get_data_from_request(request, capture_body=False):
    result = {
        "method": request.method,
        "url": get_url_data(request.url),
    }

    if not capture_body:
        return result

    if request.method in constants.HTTP_WITH_BODY:
        body = ""
        if request.content_type == "application/x-www-form-urlencoded":
            body = compat.multidict_to_dict(request.form)
        elif request.content_type and request.content_type.startswith("multipart/form-data"):
            body = compat.multidict_to_dict(request.form)
        else:
            try:
                body = request.get_data(as_text=True)
            except Exception:
                pass

        if body:
            result["body"] = body
            result["body_size"] = len(body)

    result["headers"] = dict(get_headers(request.environ))

    return result


def get_data_from_response(response, capture_body=False):
    result = {}

    if isinstance(getattr(response, "status_code", None), compat.integer_types):
        result["status_code"] = response.status_code
    elif isinstance(getattr(response, "status", None), compat.integer_types):
        result["status_code"] = response.status
    elif isinstance(getattr(response, "code", None), compat.integer_types):
        result["status_code"] = response.code

    if not capture_body:
        return result

    body = ""
    try:
        body = response.get_data(as_text=True)
    except Exception:
        pass

    result["body"] = body
    result["body_size"] = len(body)

    if getattr(response, "headers", None):
        headers = response.headers
        result["headers"] = {key: ";".join(headers.getlist(key)) for key in compat.iterkeys(headers)}

    return result


def get_data_from_exception():
    return {
        'status_code': 500,
    }
