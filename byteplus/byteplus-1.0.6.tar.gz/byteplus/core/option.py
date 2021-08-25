import datetime
from abc import abstractmethod

from byteplus.core.options import _Options


class Option(object):
    @abstractmethod
    def fill(self, options: _Options) -> None:
        raise NotImplementedError

    @staticmethod
    def conv_to_options(opts: tuple) -> _Options:
        options: _Options = _Options()
        for opt in opts:
            opt.fill(options)
        return options

    @staticmethod
    def with_timeout(timeout: datetime.timedelta):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.timeout = timeout

        return OptionImpl()

    @staticmethod
    def with_request_id(request_id: str):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.request_id = request_id

        return OptionImpl()

    @staticmethod
    def with_headers(headers: dict):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.headers = headers

        return OptionImpl()

    @staticmethod
    def with_data_date(date: datetime):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.data_date = date

        return OptionImpl()

    @staticmethod
    def with_data_end(end: bool):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.date_end = end

        return OptionImpl()

    @staticmethod
    def with_server_timeout(timeout: datetime.timedelta):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.server_timeout = timeout

        return OptionImpl()

    @staticmethod
    def with_queries(queries: dict):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.queries = queries

        return OptionImpl()

    @staticmethod
    def with_stage(stage: str):
        class OptionImpl(Option):
            def fill(self, options: _Options) -> None:
                options.stage = stage

        return OptionImpl()
