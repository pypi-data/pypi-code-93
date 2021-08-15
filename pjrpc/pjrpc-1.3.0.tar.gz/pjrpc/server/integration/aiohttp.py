"""
aiohttp JSON-RPC server integration.
"""

import json
from typing import Any, Optional
from aiohttp import web

import pjrpc
from pjrpc.server import specs, utils


class Application:
    """
    `aiohttp <https://aiohttp.readthedocs.io/en/stable/web.html>`_ based JSON-RPC server.

    :param path: JSON-RPC handler base path
    :param app_args: arguments to be passed to :py:class:`aiohttp.web.Application`
    :param kwargs: arguments to be passed to the dispatcher :py:class:`pjrpc.server.AsyncDispatcher`
    """

    def __init__(
        self,
        path: str = '',
        spec: Optional[specs.Specification] = None,
        app: Optional[web.Application] = None,
        **kwargs: Any
    ):
        self._path = path.rstrip('/')
        self._spec = spec
        self._app = app or web.Application()
        self._dispatcher = pjrpc.server.AsyncDispatcher(**kwargs)

        self._app.router.add_post(self._path, self._rpc_handle)

        if self._spec:
            self._app.router.add_get(utils.join_path(self._path, self._spec.path), self._generate_spec)

            if self._spec.ui and self._spec.ui_path:
                ui_app = web.Application()
                ui_app.router.add_get('/', self._ui_index_page)
                ui_app.router.add_get('/index.html', self._ui_index_page)
                ui_app.router.add_static('/', self._spec.ui.get_static_folder())

                self._app.add_subapp(utils.join_path(self._path, self._spec.ui_path), ui_app)

    @property
    def app(self) -> web.Application:
        """
        aiohttp application.
        """

        return self._app

    @property
    def dispatcher(self) -> pjrpc.server.Dispatcher:
        """
        JSON-RPC method dispatcher.
        """

        return self._dispatcher

    async def _generate_spec(self, request: web.Request) -> web.Response:
        spec_full_path = utils.remove_suffix(request.path, suffix=self._spec.path)
        schema = self._spec.schema(path=spec_full_path, methods=self._dispatcher.registry.values())

        return web.json_response(text=json.dumps(schema, indent=2, cls=specs.JSONEncoder))

    async def _ui_index_page(self, request: web.Request) -> web.Response:
        app_path = request.path.rsplit(self._spec.ui_path, maxsplit=1)[0]
        spec_full_path = utils.join_path(app_path, self._spec.path)

        return web.Response(
            text=self._spec.ui.get_index_page(spec_url=spec_full_path),
            content_type='text/html',
        )

    async def _rpc_handle(self, http_request: web.Request) -> web.Response:
        """
        Handles JSON-RPC request.

        :param http_request: :py:class:`aiohttp.web.Response`
        :returns: :py:class:`aiohttp.web.Request`
        """

        if http_request.content_type != 'application/json':
            raise web.HTTPUnsupportedMediaType()

        try:
            request_text = await http_request.text()
        except UnicodeDecodeError as e:
            raise web.HTTPBadRequest() from e

        response_text = await self._dispatcher.dispatch(request_text, context=http_request)
        if response_text is None:
            return web.Response()
        else:
            return web.json_response(text=response_text)
