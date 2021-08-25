import os

from jupyter_server.base.handlers import JupyterHandler
from jupyter_server.extension.handler import ExtensionHandlerMixin, ExtensionHandlerJinjaMixin
from jupyter_server.utils import url_escape


class DefaultHandler(ExtensionHandlerMixin, JupyterHandler):
    def get(self):
        # The name of the extension to which this handler is linked.
        self.log.info("Extension Name in {} default handler: {}".format(self.name, self.name))
        # A method for getting the url to static files (prefixed with /static/<name>).
        self.log.info("Static URL for {} in jupytery_react default handler:".format(self.static_url(path='/')))
        self.write('<h1>Jupytery React Extension</h1>')
        self.write('Configuration in {} default handler: {}'.format(self.name, self.config))


class BaseTemplateHandler(ExtensionHandlerJinjaMixin, ExtensionHandlerMixin, JupyterHandler):
    pass


class PlotlyHandler(BaseTemplateHandler):
    plotly_js = ''

    def get(self):
        if self.plotly_js == '':
            f = open(os.path.join(os.path.dirname(__file__), "static/plotly-2.3.0.min.js"), "r")
            self.plotly_js = f.read()
        self.set_header("Content-Type", 'text/javascript; charset="utf-8"')
        self.write(self.plotly_js)


class ErrorHandler(BaseTemplateHandler):
    def get(self, path):
        self.write(self.render_template('error.html', path=path))
