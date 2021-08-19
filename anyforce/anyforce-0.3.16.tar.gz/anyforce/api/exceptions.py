from typing import Any, List, Optional, Tuple, Union

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from pydantic import (
    AnyStrMaxLengthError,
    EmailError,
    IntegerError,
    MissingError,
    UrlError,
    ValidationError,
)
from pydantic.error_wrappers import ErrorWrapper
from tortoise import exceptions

from ..model import BaseModel
from ..model.enum import EnumMissingError

HTTPForbiddenError = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail={"errors": "禁止访问"}
)
HTTPNotFoundError = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail={"errors": "不存在"}
)
HTTPUnAuthorizedError = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail={"errors": "未认证"}
)


ValidateError = Union[RequestValidationError, ErrorWrapper, ValidationError]


def translate_validation_error(e: ValidationError) -> List[str]:
    msgs: List[str] = []
    model: Any = getattr(e, "model")
    raw_errors: List[Any] = getattr(e, "raw_errors")
    for raw_error in raw_errors:
        if isinstance(raw_error, ErrorWrapper):
            inner_exc = getattr(raw_error, "exc")

            if isinstance(inner_exc, ValidationError):
                msgs = msgs + translate_validation_error(inner_exc)
                continue

            translated_msg = ""
            if isinstance(inner_exc, MissingError):
                translated_msg = "是必填项"
            elif isinstance(inner_exc, IntegerError):
                translated_msg = "为无效的整数"
            elif isinstance(inner_exc, EmailError):
                translated_msg = "为无效的邮箱地址"
            elif isinstance(inner_exc, UrlError):
                translated_msg = "为无效的链接"
            elif isinstance(inner_exc, AnyStrMaxLengthError):
                translated_msg = "数据过长"
            # TODO: tranlstate more if needed

            if translated_msg:
                for loc in raw_error.loc_tuple():
                    property = model.schema().get("properties", {}).get(loc, {})
                    title: str = (
                        property.get("description") or property.get("title") or str(loc)
                    )
                    msgs.append(f"{title} {translated_msg}")
                continue
        msgs.append(str(raw_error))
    return msgs


def translate_validate_error(
    e: Union[ValidationError, List[ValidationError]]
) -> List[str]:
    msgs: List[str] = []
    errors: List[Any] = e if isinstance(e, List) else [e]
    for error in errors:
        msgs += translate_validation_error(error)
    return msgs


def translate_orm_error(
    e: exceptions.BaseORMException,
) -> Tuple[int, List[str]]:
    if isinstance(e, exceptions.IntegrityError):
        status_code = status.HTTP_400_BAD_REQUEST
        args: List[str] = []
        for arg in e.args:
            arg = str(arg)
            if arg.find("UNIQUE constraint failed") >= 0:
                parts = arg.split(":")[-1].split(".")
                model_name = parts[0].strip().title()
                field_name = parts[-1].strip()
                model, field = BaseModel.get_field(model_name, field_name)
                field_name = field and getattr(field, "description", None) or field_name
                model_name = model and getattr(model, "title", model.__name__) or "对象"
                args.append(f"相同 {field_name} 的{model_name}已存在")
                status_code = status.HTTP_409_CONFLICT
            else:
                args.append(arg)
        return status_code, args
    if isinstance(e, exceptions.ValidationError):
        return status.HTTP_400_BAD_REQUEST, [str(args) for args in e.args]
    if isinstance(e, exceptions.DoesNotExist):
        return status.HTTP_404_NOT_FOUND, ["不存在"]
    raise e


def handlers():
    async def validationErrorHandle(
        request: Optional[Request], exc: ValidationError
    ) -> ORJSONResponse:
        return ORJSONResponse(
            {"detail": {"errors": translate_validate_error(exc)}},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    async def ormException(
        request: Optional[Request], exc: exceptions.BaseORMException
    ) -> ORJSONResponse:
        status_code, msgs = translate_orm_error(exc)
        return ORJSONResponse(
            {"detail": {"errors": msgs}},
            status_code=status_code,
        )

    async def enumMissingErrorHandle(
        request: Optional[Request], exc: EnumMissingError
    ) -> ORJSONResponse:
        return ORJSONResponse(
            {"detail": {"errors": [str(args) for args in exc.args]}},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return (
        ([RequestValidationError, ValidationError], validationErrorHandle),
        ([exceptions.BaseORMException], ormException),
        ([EnumMissingError], enumMissingErrorHandle),
    )


def register(app: FastAPI):
    for (errors, handler) in handlers():
        for e in errors:
            app.exception_handler(e)(handler)  # type: ignore
