from aiohttp import web

from dazzler.system import Page, filter_dev_requirements


class Engine:
    def __init__(self, app):
        """
        :param app: The dazzler application.
        :type app: dazzler.Dazzler
        """
        self.app = app
        self.config = app.config
        self.logger = app.logger
        self.debug = app.config.debug

    async def render_index(
        self,
        page: Page,
        request: web.Request = None
    ) -> str:
        raise NotImplementedError

    async def get_page_json(
        self,
        page: Page,
        request: web.Request = None
    ) -> dict:
        prepared = await page.prepare(
            request,
            self.debug,
            external=self.config.requirements.prefer_external
        )
        # Add global requirements first.
        prepared['requirements'] = [
           x.prepare(
               external=self.config.requirements.prefer_external
           ) for x in filter_dev_requirements(
                self.app.requirements, self.debug)
        ] + prepared['requirements']

        if self.config.development.reload:
            # Reload mode needs the websocket even if no binding.
            prepared['reload'] = True
        return prepared
