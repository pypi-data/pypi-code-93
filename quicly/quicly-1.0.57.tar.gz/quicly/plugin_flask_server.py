from typing import *

import flask
from quicly.server import QxServerHook, QxServer, QxRequest, QxResponse
from quicly.session import QxSessionFactory


class QxFlaskServerHook(QxServerHook):
  def render_template(self, name, **kw):
    return flask.render_template(name, **kw)


class QxFlaskServerApp(object):
  def __init__(
      self,
      name: Optional[str] = None,
      hook: Optional[QxServerHook] = None,
      port: int = 8080,
      host: str = '0.0.0.0',
      debug: bool = True,
      **kw,
  ):
    self.name = name
    self.hook = hook if isinstance(hook, QxServerHook) else QxFlaskServerHook()
    self.port = port
    self.host = host
    self.debug = debug
    self.static_url_path = kw.get('static_url_path', '/static/')
    self.static_folder = kw.get('static_folder', 'static')
    self.template_folder = kw.get('template_folder', 'templates')
    self.flask_app = flask.Flask(
      f'QUICLY.{self.name}' if isinstance(self.name, str) and len(self.name) else 'QUICLY',
      static_url_path=self.static_url_path,
      static_folder=self.static_folder,
      template_folder=self.template_folder,
    )
    self.server = QxServer(self.name, self.hook)
    self.flask_app.before_request(self._handle)
    self.flask_app.after_request(self._after_request)

  def _is_static_request(self):
    return isinstance(self.static_url_path, str) and len(self.static_url_path) and flask.request.path.startswith(self.static_url_path)

  def _handle(self):
    if self._is_static_request():
      return

    method = flask.request.method.upper()
    url = flask.request.url
    headers = dict()
    cookies = dict()
    body = flask.request.data
    form = dict()
    files = list()

    for k, v in flask.request.headers.items():
      headers[k] = v

    for k, v in flask.request.cookies.items():
      cookies[k] = v

    for k, v in flask.request.form.items():
      form[k] = v

    for file in flask.request.files:
      files.append(file)

    request = QxRequest(
      method=method,
      url=url,
      headers=headers,
      cookies=cookies,
      body=body,
      form=form,
      files=files,
    )

    response = self.server.handle(request)  # type: QxResponse

    res = flask.make_response(response.data, 200 if response.code == 0 else response.code, response.headers)
    for k, v in response.cookies.items():
      if v is None:
        res.delete_cookie(k)
      else:
        res.set_cookie(k, v)
    return res

  def _after_request(self, res):
    if self._is_static_request():
      res.headers.set('Server', QxServer.get_http_header_server_name())
    return res

  @staticmethod
  def _disable_flask_logging():
    import logging
    logger = logging.getLogger('werkzeug')
    logger.setLevel(logging.ERROR)

  def run(self):
    if not self.debug:
      self._disable_flask_logging()
    self.server.init()
    self.flask_app.run(host=self.host, port=self.port, debug=self.debug)
