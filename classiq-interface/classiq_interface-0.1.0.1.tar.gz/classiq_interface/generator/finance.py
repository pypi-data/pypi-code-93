from typing import Union

import pydantic
from classiq_interface.finance.function_input import FinanceFunctionInput
from classiq_interface.finance.model_input import FinanceModelInput
from classiq_interface.generator import function_params


class Finance(function_params.FunctionParams):
    model: FinanceModelInput = pydantic.Field(description="Load a financial model")
    finance_function: Union[FinanceFunctionInput] = pydantic.Field(
        description="The finance function to solve the model"
    )
