import base64
import gzip
import json
import logging
try:
    from cStringIO import StringIO
except Exception:
    try:
        from StringIO import StringIO
    except Exception:
        pass  # python 3, we use a new function in gzip

from stackifyapm.transport.base import BaseTransport


def gzip_compress(data):
    if hasattr(gzip, 'compress'):
        return gzip.compress(bytes(data, 'utf-8'), compresslevel=6)  # python 3
    else:
        s = StringIO()
        g = gzip.GzipFile(fileobj=s, mode='w', compresslevel=6)
        g.write(data)
        g.close()
        return s.getvalue()


def compress(data):
    compressed_data = gzip_compress(data)
    return base64.b64encode(compressed_data).decode("utf-8")


class LoggingTransport(BaseTransport):
    """
    Serverless Logging Transport handles logging of transaction data into console
    """
    def __init__(self, client):
        self._client = client
        # if lambda_handler is not empty use named logger for AWS Lambda
        # if not then use root logging for Azure Function
        if self._client.config.lambda_handler:
            self.logging = logging.getLogger("stackify_severless")
            self.logging.setLevel(level=logging.DEBUG)
            self.logging.addHandler(self._console_handler())
            self.logging.propagate = False
        else:
            self.logging = logging

    def _console_handler(self):
        handler = logging.StreamHandler()
        handler.setLevel(level=logging.DEBUG)
        handler.setFormatter(logging.Formatter('STACKIFY-TRACE: %(message)s'))
        return handler

    def send_all(self):
        # nothing to do in here since we do log transaction immediately once done
        pass

    def log_transaction(self, transaction):
        # log transaction immediately
        config = self._client and self._client.config or None
        json_string_trace = json.dumps(transaction.to_dict(config=config))
        compressed_data = compress(json_string_trace)
        if self._client.config.lambda_handler:
            self.logging.debug(compressed_data)
        else:
            self.logging.info("STACKIFY-TRACE: {}".format(compressed_data))
