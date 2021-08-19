import logging
import os
import sys
import threading
from typing import Callable

from django.conf import settings
from django.http import HttpRequest, HttpResponse

from .db import setup_db
from .profiler import KoloProfiler

logger = logging.getLogger("kolo")

DjangoView = Callable[[HttpRequest], HttpResponse]


class KoloMiddleware:
    def __init__(self, get_response: DjangoView) -> None:
        self.get_response = get_response
        self.enabled = self.should_enable()
        if self.enabled:
            self.db_path = setup_db()

    def __call__(self, request: HttpRequest) -> HttpResponse:
        if not self.enabled:
            return self.get_response(request)

        if self.check_for_third_party_profiler():
            return self.get_response(request)

        profiler = KoloProfiler(self.db_path)
        profiler.initialize_request(request)

        with profiler:
            response = self.get_response(request)

        profiler.finalize_response(response)

        threading.Thread(target=profiler.save_request_in_db).start()

        # eventual todo: restore previously set profile
        return response

    def check_for_third_party_profiler(self) -> bool:
        profiler = sys.getprofile()
        if profiler:
            logger.warning("Profiler %s is active, disabling KoloMiddleware", profiler)
            return True
        return False

    def should_enable(self) -> bool:
        if settings.DEBUG is False:
            logger.debug("DEBUG mode is off, disabling KoloMiddleware")
            return False

        if os.environ.get("KOLO_DISABLE", "false").lower() not in ["false", "0"]:
            logger.debug("KOLO_DISABLE is set, disabling KoloMiddleware")
            return False

        if self.check_for_third_party_profiler():
            return False

        return True
