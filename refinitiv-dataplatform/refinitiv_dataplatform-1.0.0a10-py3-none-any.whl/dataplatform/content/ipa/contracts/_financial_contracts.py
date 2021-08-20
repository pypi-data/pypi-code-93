# coding: utf8

__all__ = ["FinancialContracts"]

from enum import Enum, unique
from refinitiv.dataplatform.tools._common import urljoin
from refinitiv.dataplatform.delivery.data import Endpoint
from refinitiv.dataplatform.content.ipa.instrument import InstrumentDefinition
from refinitiv.dataplatform.content.ipa.instrument import InstrumentCalculationParams


class FinancialContracts(Endpoint):
    @unique
    class Outputs(Enum):
        HEADERS = "Headers"
        DATATYPE = "DataType"
        DATA = "Data"
        STATUSES = "Statuses"
        MARKET_DATA = "MarketData"

    def __init__(self, session=None, on_response=None):
        from refinitiv.dataplatform.legacy.tools import DefaultSession

        session = session or DefaultSession.get_default_session()
        config = session._get_endpoint_config(
            "data.quantitative-analytics-financial-contracts"
        )
        base_url = config.get_str("url")
        url_contracts = config.get_str("endpoints.financial-contracts")
        super().__init__(
            session,
            urljoin(base_url, url_contracts),
            on_response=on_response,
            service_class=InstrumentDefinition,
        )

    def _get_instrument_analytics(
        self, universe, fields=None, calculation_params=None, outputs=None, closure=None
    ):
        if self.session is not None:
            result = self.session._loop.run_until_complete(
                self._get_instrument_analytics_async(
                    universe=universe,
                    fields=fields,
                    calculation_params=calculation_params,
                    outputs=outputs,
                    closure=closure,
                )
            )
            return result

    async def _get_instrument_analytics_async(
        self, universe, fields=None, calculation_params=None, outputs=None, closure=None
    ):
        if self.session is None:
            return None

        fields = fields or []

        if not isinstance(universe, list):
            universe = [universe]

        if not (
            all(
                isinstance(instrument, InstrumentDefinition)
                or (
                    type(instrument) == tuple
                    and len(instrument) == 2
                    and isinstance(instrument[0], InstrumentDefinition)
                    and isinstance(instrument[1], InstrumentCalculationParams)
                )
            )
            for instrument in universe
        ):
            raise ValueError(
                "all universe items must be Instrument or tuple(Instrument, InstrumentParameters)"
            )

        if isinstance(fields, list):
            # if not all((isinstance(field, Enum) or isinstance(field, str)) for field in fields):
            #     raise TypeError("fields must be a list of Fields enums or strings")
            if not all(isinstance(field, str) for field in fields):
                raise TypeError("fields must be a list of strings")
        # Convert all Field enum values into str
        # _fields = [f.value if isinstance(f, Enum) else f for f in fields]
        _fields = fields

        _universe = []

        # convert universe's objects into json
        for i, item in enumerate(universe):
            if isinstance(item, InstrumentDefinition):
                data = {
                    "instrumentType": item.get_instrument_type(),
                    "instrumentDefinition": item.get_json(),
                }
            else:  # item is a tuple (instrument, calculation_params)
                instrument, calculation_params = item
                data = {
                    "instrumentType": instrument.get_instrument_type(),
                    "instrumentDefinition": instrument.get_json(),
                    "pricingParameters": calculation_params.get_json(),
                }
            _universe.append(data)

        _body_parameters = {"fields": _fields, "universe": _universe}

        if outputs:
            _outputs = [
                item.value if isinstance(item, FinancialContracts.Outputs) else item
                for item in outputs
            ]
            _body_parameters["outputs"] = _outputs

        if calculation_params:
            _body_parameters["pricingParameters"] = calculation_params.get_json()

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
    def get_instrument_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        _ipa = FinancialContracts(session=session, on_response=on_response)
        return _ipa._get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )

    @staticmethod
    async def get_instrument_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    ##########################################################
    #  Functions specific for Bond
    ##########################################################

    @staticmethod
    def _check_bond_universe(universe):
        from refinitiv.dataplatform.content.ipa import bond

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            bond.Definition(item) if isinstance(item, str) else item
            for item in universe
        ]

        if not all(
            isinstance(bond_definition, bond.Definition)
            or (
                type(bond_definition) == tuple
                and len(bond_definition) == 2
                and isinstance(bond_definition[0], bond.Definition)
                and isinstance(bond_definition[1], bond.CalculationParams)
            )
            for bond_definition in universe
        ):
            raise ValueError(
                "all universe items must be bond.Definition or tuple(bond.Definition, bond.CalculationParams)"
            )
        return universe

    @staticmethod
    def get_bond_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_bond_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_bond_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_bond_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    ##########################################################
    #  Functions specific for Option
    ##########################################################

    @staticmethod
    def _check_option_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.option import Definition
        from refinitiv.dataplatform.content.ipa.contracts.option import (
            CalculationParams,
        )

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(item) if isinstance(item, str) else item for item in universe
        ]

        if not all(
            isinstance(option_definition, Definition)
            or (
                type(option_definition) == tuple
                and len(option_definition) == 2
                and isinstance(option_definition[0], Definition)
                and isinstance(option_definition[1], CalculationParams)
            )
            for option_definition in universe
        ):
            raise ValueError("All universe instruments must be Option Definition")
        return universe

    @staticmethod
    def _check_swap_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.swap import Definition
        from refinitiv.dataplatform.content.ipa.contracts.swap import CalculationParams

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(item) if isinstance(item, str) else item for item in universe
        ]

        if not all(
            isinstance(swap_definition, Definition)
            or (
                type(swap_definition) == tuple
                and len(swap_definition) == 2
                and isinstance(swap_definition[0], Definition)
                and isinstance(swap_definition[1], CalculationParams)
            )
            for swap_definition in universe
        ):
            raise ValueError("All universe instruments must be Swap Definition")
        return universe

    @staticmethod
    def _check_cds_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.cds import Definition
        from refinitiv.dataplatform.content.ipa.contracts.cds import CalculationParams

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(item) if isinstance(item, str) else item for item in universe
        ]

        if not all(
            isinstance(cds, Definition)
            or (
                type(cds) == tuple
                and len(cds) == 2
                and isinstance(cds[0], Definition)
                and isinstance(cds[1], CalculationParams)
            )
            for cds in universe
        ):
            raise ValueError("All universe instruments must be Cds Definition")
        return universe

    @staticmethod
    def _check_cross_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.cross import Definition
        from refinitiv.dataplatform.content.ipa.contracts.cross import CalculationParams

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(instrument_tag=item) if isinstance(item, str) else item
            for item in universe
        ]

        if not all(
            isinstance(cds, Definition)
            or (
                type(cds) == tuple
                and len(cds) == 2
                and isinstance(cds[0], Definition)
                and isinstance(cds[1], CalculationParams)
            )
            for cds in universe
        ):
            raise ValueError("All universe instruments must be Cross Definition")
        return universe

    @staticmethod
    def _check_repo_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.repo import Definition
        from refinitiv.dataplatform.content.ipa.contracts.repo import CalculationParams

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(instrument_tag=item) if isinstance(item, str) else item
            for item in universe
        ]

        if not all(
            isinstance(repo, Definition)
            or (
                type(repo) == tuple
                and len(repo) == 2
                and isinstance(repo[0], Definition)
                and isinstance(repo[1], CalculationParams)
            )
            for repo in universe
        ):
            raise ValueError("All universe instruments must be Repo Definition")
        return universe

    @staticmethod
    def _check_capfloor_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.capfloor import Definition
        from refinitiv.dataplatform.content.ipa.contracts.capfloor import (
            CalculationParams,
        )

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(instrument_tag=item) if isinstance(item, str) else item
            for item in universe
        ]

        if not all(
            isinstance(capfloor, Definition)
            or (
                type(capfloor) == tuple
                and len(capfloor) == 2
                and isinstance(capfloor[0], Definition)
                and isinstance(capfloor[1], CalculationParams)
            )
            for capfloor in universe
        ):
            raise ValueError("All universe instruments must be capfloor Definition")
        return universe

    @staticmethod
    def _check_swaption_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.swaption import Definition
        from refinitiv.dataplatform.content.ipa.contracts.swaption import (
            CalculationParams,
        )

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(instrument_tag=item) if isinstance(item, str) else item
            for item in universe
        ]

        if not all(
            isinstance(swaption, Definition)
            or (
                type(swaption) == tuple
                and len(swaption) == 2
                and isinstance(swaption[0], Definition)
                and isinstance(swaption[1], CalculationParams)
            )
            for swaption in universe
        ):
            raise ValueError("All universe instruments must be swaption Definition")
        return universe

    @staticmethod
    def _check_term_deposit_universe(universe):
        from refinitiv.dataplatform.content.ipa.contracts.term_deposit import Definition
        from refinitiv.dataplatform.content.ipa.contracts.term_deposit import (
            CalculationParams,
        )

        if not isinstance(universe, list):
            universe = [universe]

        universe = [
            Definition(instrument_tag=item) if isinstance(item, str) else item
            for item in universe
        ]

        if not all(
            isinstance(term_deposit, Definition)
            or (
                type(term_deposit) == tuple
                and len(term_deposit) == 2
                and isinstance(term_deposit[0], Definition)
                and isinstance(term_deposit[1], CalculationParams)
            )
            for term_deposit in universe
        ):
            raise ValueError("All universe instruments must be term_deposit Definition")
        return universe

    @staticmethod
    def get_option_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_option_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_option_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_option_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_swap_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_swap_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_swap_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_swap_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_cds_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_cds_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_cds_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_cds_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_cross_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_cross_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_cross_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_cross_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_repo_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_repo_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_repo_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_repo_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_capfloor_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_capfloor_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_capfloor_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_capfloor_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_swaption_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_swaption_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_swaption_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_swaption_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    def get_term_deposit_analytics(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_term_deposit_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = _ipa.get_instrument_analytics(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result

    @staticmethod
    async def get_term_deposit_analytics_async(
        universe,
        fields=None,
        calculation_params=None,
        outputs=None,
        on_response=None,
        closure=None,
        session=None,
    ):
        universe = FinancialContracts._check_term_deposit_universe(universe)
        _ipa = FinancialContracts(session=session, on_response=on_response)
        result = await _ipa._get_instrument_analytics_async(
            universe=universe,
            fields=fields,
            calculation_params=calculation_params,
            outputs=outputs,
            closure=closure,
        )
        return result
