# coding: utf8

__all__ = ["Curves"]

from enum import Enum, unique

from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.tools._common import is_all_same_type, urljoin
from ._curve_definition import CurveDefinition


class Curves(Endpoint):
    @unique
    class Outputs(Enum):
        CONSTITUENTS = "Constituents"
        DETAILED_CURVE_POINT = "DetailedCurvePoint"

    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session or DefaultSession.get_default_session()
        config = session._get_endpoint_config(
            "data.quantitative-analytics-curves-and-surfaces"
        )
        base_url = config.get_str("url")
        url_curves = config.get_str("endpoints.forward-curves")
        super().__init__(
            session,
            urljoin(base_url, url_curves),
            on_response=on_response,
            service_class=CurveDefinition,
        )

    def _run_until_complete(self, future):
        return self.session._loop.run_until_complete(future)

    def _get_curve(self, universe, outputs=None, closure=None):
        """
        :param universe:list    The list of Volatility Surface Definitions
        :param outputs:enum     The Requested outputs. Optional. By default only data are returned.
        :param closure:str
        :return:Response
        """
        result = self._run_until_complete(
            self._get_curve_async(universe=universe, outputs=outputs, closure=closure)
        )
        return result

    async def _get_curve_async(self, universe, outputs=None, closure=None):
        """
        :param universe:list    The list of Volatility Surface Definitions
        :param outputs:enum     The Requested outputs. Optional. By default only data are returned.
        :param closure:str
        :return:Response
        """
        if not isinstance(universe, list):
            universe = [universe]

        if not is_all_same_type(CurveDefinition, universe):
            raise ValueError("all universe items must be Instrument")

        _universe = []

        # convert universe's objects into json
        for i, instrument in enumerate(universe):
            _universe.append(instrument.get_json())

        _body_parameters = {"universe": _universe}

        if outputs:
            _outputs = [
                item.value if isinstance(item, Curves.Outputs) else item
                for item in outputs
            ]
            _body_parameters["outputs"] = _outputs

        self.session.log(1, f"Request analytic :\n {_body_parameters}")
        _result = await self.send_request_async(
            Endpoint.RequestMethod.POST,
            body_parameters=_body_parameters,
            closure=closure,
        )
        if _result and not _result.is_success:
            self.session.log(1, f"Instrument request failed: {_result.status}")

        return _result

    @staticmethod
    def get_curve(universe, outputs=None, on_response=None, closure=None, session=None):
        surfaces = Curves(session=session, on_response=on_response)
        result = surfaces._get_curve(
            universe=universe, outputs=outputs, closure=closure
        )
        return result

    @staticmethod
    async def get_curves_async(
        universe, outputs=None, on_response=None, closure=None, session=None
    ):
        surfaces = Curves(session=session, on_response=on_response)
        result = await surfaces._get_curve_async(
            universe=universe, outputs=outputs, closure=closure
        )
        return result
