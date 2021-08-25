import sys
import re

from tornado.web import authenticated

from jupyterhub.handlers.base import BaseHandler

from .version import __version__


class AdminHandler(BaseHandler):
    @authenticated
    async def get(self):
#        current_user = await self.get_current_user()
        html = self.render_template(
            "jupytery-admin.html",
            base_url=self.settings['base_url'],
            jupyterhub_api_token='3bae6566e7314d8a84b65b7d92420ee7'
        )
        template_html = await html
        self.write(template_html)
