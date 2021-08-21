from pythonidae.request import Request
import json

import jinja2
jinja_template = jinja2.Environment(
    loader=jinja2.FileSystemLoader('./')
)

# todo: Add more content types for various files
file_content_types = {
    'html': 'text/html',
    'htm':  'text/html',
    'css':  'text/css',
    'js':   'text/javascript',
    'mkv':  'video/mkv',
    'jpg': 'image/jpeg'
}

status_code_name = {
    200: '200 OK',
    301: '301 Moved Permanently',
    400: '400 Bad Request',
    404: '404 Not Found',
    500: '500 Internal Server Error',
}


class Response:
    # Base Response Class

    __slots__ = 'headers', 'status_code', 'start_response', 'content_type', 'response_content', 'response_headers'

    def __init__(self, request: Request, status_code: str, content_type: str):
        self.headers = []
        self.status_code = status_code
        self.start_response = request.start_response
        self.content_type = content_type
        self.response_content = []
        self.response_headers = []

    def make_response(self):
        self.start_response(self.status_code, self.response_headers)
        return self.response_content


class HttpResponse(Response):
    # Return pure http response when given a text as content

    def __init__(self, request: Request, content, status_code=200, content_type='text/plain', send_headers=[], cookies=[]):
        super().__init__(request, status_code_name.get(
            status_code, str(status_code) + " "), content_type)
        if type(content) == str:
            content = content.encode()
        self.response_content.append(content)

        self.response_headers = []
        self.response_headers.append(('Content-Type', self.content_type))
        for l in send_headers:
            self.response_headers.append(l)

        for c in cookies:
            self.response_headers.append(('Set-Cookie', c))


class HttpResponseRedirect(Response):

    def __init__(self, request: Request, location):
        super().__init__(request, "301 ", "text/plain")
        self.response_content.append("".encode())
        self.response_headers = []
        self.response_headers.append(('Location', location))


class RenderResponse(Response):
    # Uses HttpResponse to return http response given a template name and context dict
    # Todo: Implement a way to render dynamic content from the context into templates

    def __init__(self, request: Request, filename: str, context: dict = {}, status_code=200, content_type='text/plain', send_headers=[], cookies=[]):
        
        template_content = ""

        try:
            with open(filename, 'r') as f:
                text = f.read()
        except FileNotFoundError:
            print(f'Error openning file {filename}')
            raise Exception(f'Could not find the file {filename}')

        template_content = jinja_template.from_string(text).render(context)

        super().__init__(request, status_code_name.get(status_code, str(status_code) + " "), content_type)
        self.response_content.append(template_content.encode())

        self.response_headers = []
        self.response_headers.append(('Content-Type', self.content_type))
        for l in send_headers:
            self.response_headers.append(l)

        for c in cookies:
            self.response_headers.append(('Set-Cookie', c))


class JsonResponse(Response):
    # Return pure json response when given a text as content

    def __init__(self, request: Request, content, status_code=200, content_type='application/json', send_headers=[], cookies=[]):
        content = json.dumps(content)
        super().__init__(request, status_code_name.get(
            status_code, str(status_code) + " "), content_type)
        self.response_content.append(content.encode())

        self.response_headers = []
        self.response_headers.append(('Content-Type', self.content_type))
        for l in send_headers:
            self.response_headers.append(l)

        for c in cookies:
            self.response_headers.append(('Set-Cookie', c))


class FileResponse(Response):
    def __init__(self,  request: Request, filename: str, file_root: str = "", send_headers=[], cookies=[]):
        try:
            with open(file_root+filename, 'rb') as f:
                content = f.read()
        except FileNotFoundError:
            print(f'File not found {filename}')
            raise Exception(f'could not find the file {filename}')

        content_type = file_content_types.get(
            filename.split('.')[-1], 'text/plain')

        super().__init__(request, '200 OK', content_type)
        self.response_content.append(content)

        self.response_headers = []
        self.response_headers.append(('Content-Type', self.content_type))
        for l in send_headers:
            self.response_headers.append(l)

        for c in cookies:
            self.response_headers.append(('Set-Cookie', c))


class ErrorResponse(Response):
    def __init__(self, request: Request, error_code: str, send_headers=[], cookies=[]):
        super().__init__(request, '404 Not Found', 'text/plain')
        self.response_content.append("404 Not Found".encode())

        self.response_headers = []
        self.response_headers.append(('Content-Type', self.content_type))
        for l in send_headers:
            self.response_headers.append(l)

        for c in cookies:
            self.response_headers.append(('Set-Cookie', c))


class Http404(ErrorResponse):
    def __init__(self, request):
        super().__init__(request, '404 Not Found')
