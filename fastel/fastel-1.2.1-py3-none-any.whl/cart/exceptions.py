from fastapi.requests import Request
from fastapi.responses import JSONResponse


class CartException(Exception):
    pass


def cart_exception_handler(request: Request, exc: CartException) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"error": str(exc), "detail": ""},
    )
