# coding: utf8

__all__ = ["Symbology"]

from .symbol_type import SymbolTypes, SYMBOL_TYPE_VALUES
from ..search import Lookup, SearchViews


class Symbology(object):
    SymbolTypes = SymbolTypes

    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import get_default_session

        if session is None:
            session = get_default_session()

        if session is None:
            raise AttributeError("A Session must be started")

        self._on_response_cb = on_response
        self._data = None
        self._lookup = Lookup(session=session, onResponseCallbackFunc=self._on_response)

    @property
    def data(self):
        return self._data

    @property
    def status(self):
        if self._data:
            return self._data.status
        return {}

    def _on_response(self, endpoint, data):
        self._data = data
        if self._on_response_cb:
            self._on_response_cb(self, data)

    @staticmethod
    def convert(
        symbols,
        from_symbol_type=SymbolTypes.RIC,
        to_symbol_types=None,
        on_response=None,
        closure=None,
    ):
        symbology = Symbology(on_response=on_response)
        response = symbology._convert(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
        )
        return response

    @staticmethod
    async def convert_async(
        symbols,
        from_symbol_type=SymbolTypes.RIC,
        to_symbol_types=None,
        on_response=None,
        closure=None,
    ):
        symbology = Symbology(on_response=on_response)
        response = await symbology._convert_async(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
        )
        return response

    def _convert(
        self,
        symbols,
        from_symbol_type=SymbolTypes.RIC,
        to_symbol_types=None,
        closure=None,
    ):
        return self._lookup._endpoint.session._loop.run_until_complete(
            self._convert_async(
                symbols=symbols,
                from_symbol_type=from_symbol_type,
                to_symbol_types=to_symbol_types,
                closure=closure,
            )
        )

    async def _convert_async(
        self,
        symbols,
        from_symbol_type=SymbolTypes.RIC,
        to_symbol_types=None,
        closure=None,
    ):
        return await self.__convert(
            symbols=symbols,
            from_symbol_type=from_symbol_type,
            to_symbol_types=to_symbol_types,
            closure=closure,
        )

    async def __convert(
        self,
        symbols,
        from_symbol_type=SymbolTypes.RIC,
        to_symbol_types=None,
        closure=None,
    ):

        from_symbol_type = SymbolTypes.convert_to_str(from_symbol_type)

        select = ["DocumentTitle"]

        if to_symbol_types is None:
            select += SYMBOL_TYPE_VALUES
        elif isinstance(to_symbol_types, list):
            select = map(SymbolTypes.convert_to_str, to_symbol_types)
        elif isinstance(to_symbol_types, str):
            select.append(to_symbol_types)

        select = ",".join(select)

        if isinstance(symbols, list):
            symbols = ",".join(symbols)

        response = await self._lookup._lookup_async(
            view=SearchViews.SearchAll,
            terms=symbols,
            scope=from_symbol_type,
            select=select,
            closure=closure,
        )

        return response
