from unpoly import Unpoly
from unpoly.adapter import BaseAdapter

UP_METHOD_COOKIE = "_up_method"


class UnpolyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.up = up = Unpoly(DjangoAdapter(request))
        response = self.get_response(request)
        up.finalize_response(response)
        return response


class DjangoAdapter(BaseAdapter):
    def __init__(self, request):
        self.request = request

    def request_headers(self):
        return self.request.headers

    def request_params(self):
        return self.request.GET

    def redirect_uri(self, response):
        return (
            response.headers.get("Location")
            if 300 <= response.status_code < 400
            else False
        )

    def set_redirect_uri(self, response, uri):
        response.headers["Location"] = uri

    def set_headers(self, response, headers):
        for k, v in headers.items():
            response.headers[k] = v

    def set_cookie(self, response, needs_cookie=False):
        if needs_cookie:
            response.set_cookie(UP_METHOD_COOKIE, self.method)
        elif UP_METHOD_COOKIE in self.request.COOKIES:
            response.delete_cookie(UP_METHOD_COOKIE)

    @property
    def method(self):
        return self.request.method

    @property
    def location(self):
        return self.request.get_full_path_info()
