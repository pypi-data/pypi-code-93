from collections import namedtuple
from foreverbull_core.models.socket import Request, Response

import logging

ROUTE = namedtuple("route", "func, route, model")


class TaskNotFoundError(Exception):
    pass


class TaskAlreadyExists(Exception):
    pass


class MessageRouter:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._routes = {}

    def __call__(self, request):
        if request.task not in self._routes:
            return Response(task=request.task, error=str(TaskNotFoundError("task not found")))
        route = self._routes[request.task]
        try:
            if route.model is None:
                data = route.func()
            else:
                model_data = route.model.load(request.data)
                data = route.func(model_data)
            return Response(task=request.task, data=data)
        except Exception as exc:
            self._logger.error(f"Error calling task: {request.task}")
            self._logger.error(exc, exc_info=True)
            return Response(task=request.task, error=str(exc))

    def add_route(self, function, route, model=None):
        if route in self._routes:
            raise TaskAlreadyExists(f"{route} already registered")
        new_route = ROUTE(function, route, model)
        self._routes[route] = new_route
