"""
    output render factory
"""

from dimsum.providers.output_render.html_render import HtmlRender

class OutputRenderFactory():

    # output render factory
    @staticmethod
    def get_output_render(config):
        if config['type'] == 'html':
            return HtmlRender(config)
        else:
            raise Exception('> output render provider: %s is not supported' % (config['type']))

    # return supported meta manager info
    @staticmethod
    def info():
        return ['output_renders: html render.']