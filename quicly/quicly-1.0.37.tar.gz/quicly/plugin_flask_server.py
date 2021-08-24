import tarfile

import flask
from quicly.server import QxServer, QxRequest, QxResponse
from quicly.session import QxSessionFactory


class QuiclyServerApp(object):
  def __init__(
      self,
      name: str = None,
      port=8080,
      host='0.0.0.0',
      debug=False,
      static_url_path: str = '/static/',
      static_folder: str = 'static',
      template_folder: str = 'templates',
      session_factory: QxSessionFactory = None,
      settings=None,
  ):
    self.port = port
    self.host = host
    self.debug = debug
    self.static_url_path = static_url_path
    self.static_folder = static_folder
    self.template_folder = template_folder
    self.flask_app = flask.Flask(
      'QUICLY',
      static_url_path=static_url_path,
      static_folder=static_folder,
      template_folder=template_folder,
    )
    self.server = QxServer(name, fn_render_template=self._render_template)
    self.session_factory = session_factory
    self.settings = settings
    self.flask_app.before_request(self._handle)
    self.flask_app.after_request(self._after_request)

  def _is_static_request(self):
    return isinstance(self.static_url_path, str) and len(self.static_url_path) and flask.request.path.startswith(self.static_url_path)

  @staticmethod
  def _render_template(name: str, **kw):
    return flask.render_template(name, **kw)

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
      settings=self.settings,
    )

    if isinstance(self.session_factory, QxSessionFactory):
      request.session = self.session_factory.load_session(request.sessionid)

    response = self.server.handle(request)  # type: QxResponse

    res = flask.make_response(response.data, 200 if response.code == 0 else response.code, response.headers)
    for k, v in response.cookies.items():
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
    if isinstance(self.session_factory, QxSessionFactory):
      self.session_factory.init_session()
    self.flask_app.run(host=self.host, port=self.port, debug=self.debug)
