from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class APIException(Exception):
    def __init__(self, status_code: int, error: str, detail: Any):
        super().__init__(detail)
        self.status_code = status_code
        self.error = error
        self.detail = detail


def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "detail": exc.detail},
    )
