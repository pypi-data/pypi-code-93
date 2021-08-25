from typing import Any, TypeVar, Union, Callable
from limes_common.models.basic import AbbreviatedEnum

from limes_common.models.network import Primitive, ErrorModel, Model, provider
from limes_common.exceptions import AbstractClassException
from limes_common.utils import current_time

_notImplimentedMsg = 'Call on abstract provider. Funciton not implimented.'

class Criteria(AbbreviatedEnum):
    ALL = 0
    SAMPLES = 1
    DATA = 2

T = TypeVar('T')
class Connection:
    def __init__(self, searchableCriteria: list[Criteria]) -> None:
        self.LastUse = current_time()
        self.SearchableCriteria = searchableCriteria

    def GetSchema(self) -> provider.Schema:
        raise AbstractClassException(_notImplimentedMsg)

    def Send(self, reqModel: Model, constr: Callable[..., T]) -> Union[T, ErrorModel]:
        raise AbstractClassException(_notImplimentedMsg)

    # def CheckStatus(self, msg: str='') -> Models.Status.Response:
    #     raise AbstractClassException(_notImplimentedMsg)

    # def MakeRequest(self, purpose: str, request: Primitive) -> Primitive:
    #     raise AbstractClassException(_notImplimentedMsg)

    # def Search(self, token: Union[str, list[str]], criteria: list[Criteria]):
    #     raise AbstractClassException(_notImplimentedMsg)
