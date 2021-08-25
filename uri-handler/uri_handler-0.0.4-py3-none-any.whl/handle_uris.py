from uri_handler.errors import UriHandlerException
from uri_handler.utils._compat import urllib

from uri_handler.storage.filestorage import FileUriHandler
from uri_handler.storage.s3storage import S3UriHandler


scheme_uri_handler_classes = {
    "s3": S3UriHandler,
    "file": FileUriHandler
    }


def get_uri_handler(uri):
    p = urllib.parse.urlparse(uri)
    try:
        handler_class = scheme_uri_handler_classes[p.scheme]
    except KeyError as e:
        raise UriHandlerException(
            "Unknown uri schema {}".format(
                e))
    return handler_class()


__all__ = ["get_uri_handler", "S3UriHandler", "FileUriHandler"]
