from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from .level import SUCCESS


class Context(object):
    def __init__(
        self, logger: logging.Logger, context: Optional[Dict[str, Any]] = None
    ) -> None:
        super(Context, self).__init__()
        self.logger = logger
        self.context: Dict[str, Any] = context or {}

    def get_extras(self, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        context = self.context.copy()
        if extra:
            context.update(extra)

        # 替换特殊关键词
        for keyword in ["name", "level", "msg", "args", "exc_info", "func"]:
            val = context.pop(keyword, None)
            if val:
                context[f"{keyword}_"] = val

        return context

    def with_field(self, **kwargs: Any) -> Context:
        context = self.context.copy()
        context.update(kwargs)
        return Context(self.logger, context=context)

    def log(
        self,
        level: int,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
        stacklevel: int = 1,
    ) -> Context:
        if not self.logger.isEnabledFor(level):
            return self

        self.logger._log(  # type: ignore
            level,
            msg,
            args,
            exc_info=exc_info,
            extra=self.get_extras(extra),
            stack_info=stack_info,
            stacklevel=stacklevel,
        )
        return self

    def debug(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.DEBUG,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def info(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.INFO,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def warning(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.WARNING,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def warn(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.WARNING,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def error(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.ERROR,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def exception(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.ERROR,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def critical(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            logging.CRITICAL,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )

    def success(
        self,
        msg: str,
        *args: Any,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
    ) -> Context:
        return self.log(
            SUCCESS,
            msg,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=2,
            *args,
        )


class ContextLogger(logging.Logger):
    def with_field(self, **kwargs: Any) -> Context:
        return Context(self, context=kwargs)

    def success(
        self,
        msg: str,
        exc_info: Optional[Exception] = None,
        extra: Optional[Dict[str, Any]] = None,
        stack_info: bool = False,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        return self._log(  # type: ignore
            SUCCESS,
            msg,
            args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            **kwargs,
        )
