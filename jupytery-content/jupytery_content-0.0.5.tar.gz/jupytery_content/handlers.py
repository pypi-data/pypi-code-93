from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin, ExtensionHandlerJinjaMixin
from jupyter_server.utils import url_escape


class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):

    def get(self):
        # The name of the extension to which this handler is linked.
        self.log.info("Extension Name in {} default handler: {}".format(self.name, self.name))
        # A method for getting the url to static files (prefixed with /static/<name>).
        self.log.info("Static URL for {} in jupytery_content default handler:".format(self.static_url(path='/')))
        self.write('<h1>Jupytery Content Extension</h1>')
        self.write('Configuration in {} default handler: {}'.format(self.name, self.config))


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    pass


class ErrorHandler(BaseTemplateHandler):

    def get(self, path):
        self.write(self.render_template('error.html', path=path))
