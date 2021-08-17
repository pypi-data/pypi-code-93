import http.server
import sysconfig
from os import path


cpython_site_packages = sysconfig.get_path("purelib")


class Handler(http.server.CGIHTTPRequestHandler):

    def guess_type(self, path_):
        ctype = super().guess_type(path_)
        # in case the mimetype associated with .js in the Windows
        # registery is not correctly set
        if path.splitext(path_)[1] == ".js":
            ctype = "application/javascript"
        return ctype

    def translate_path(self, path_):
        """Map /cpython_site_packages to local CPython site-packages."""
        elts = path_.split('/')
        if len(elts) > 1 and elts[0] == '':
            if elts[1] == 'cpython_site_packages':
                elts[-1] = elts[-1].split("?")[0]
                return path.join(cpython_site_packages, *elts[2:])
        return super().translate_path(path_)


def start(port):

    print("Brython development server. Not meant to be used in production.")
    print("Press CTRL+C to Quit.")
    http.server.test(HandlerClass=Handler, port=port)
