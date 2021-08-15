import flask
from quicly.server import QxServer, QxRequest, QxResponse

# import logging
# logger = logging.getLogger('werkzeug')
# logger.setLevel(logging.ERROR)


flask_app = flask.Flask('QUICLY')

qx_server = QxServer()


def __flask_handler(*a, **kw):
  method = flask.request.method.upper()
  url = flask.request.url
  headers = dict()
  cookies = dict()
  body = flask.request.data

  for k, v in flask.request.headers.items():
    headers[k] = v

  for k, v in flask.request.cookies.items():
    cookies[k] = v

  request = QxRequest(
    method=method,
    url=url,
    headers=headers,
    cookies=cookies,
    body=body,
  )

  response = qx_server.handle(request)  # type: QxResponse

  res = flask.make_response(response.data, 200 if response.code == 0 else response.code, response.headers)
  for k, v in response.cookies.items():
    res.set_cookie(k, v)
  return res


@flask_app.route('/', methods=['GET', 'PUT', 'POST', 'HEAD', 'PATCH', 'DELETE', 'OPTIONS'])
def __flask_handler_1(*a, **kw):
  return __flask_handler(*a, **kw)


@flask_app.route('/<path:path>', methods=['GET', 'PUT', 'POST', 'HEAD', 'PATCH', 'DELETE', 'OPTIONS'])
def __flask_handler_2(path, *a, **kw):
  return __flask_handler(*a, **kw)


class QuiclyServerApp(object):
  def __init__(self, port=8080, host='0.0.0.0', debug=False):
    self.port = port
    self.host = host
    self.debug = debug

  def run(self):
    flask_app.run(host=self.host, port=self.port, debug=self.debug)
