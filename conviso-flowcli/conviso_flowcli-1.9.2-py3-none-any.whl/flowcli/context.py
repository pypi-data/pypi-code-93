import click

from convisoappsec.flow import api
from convisoappsec.version import __version__


class FlowContext(object):
    def __init__(self):
        self.key = None
        self.url = None
        self.insecure = None

    def create_flow_api_client(self):
        return api.Client(
            key=self.key,
            url=self.url,
            insecure=self.insecure,
            user_agent={
                'name': 'flowcli',
                'version': __version__,
            }
        )


pass_flow_context = click.make_pass_decorator(
    FlowContext, ensure=True
)
