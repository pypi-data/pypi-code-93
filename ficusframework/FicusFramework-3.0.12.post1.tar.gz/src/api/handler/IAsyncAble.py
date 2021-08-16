from abc import abstractmethod

from api.model.ResultVO import ResultVO
from api.model.AsyncServiceResponse import AsyncServiceResponse

class IAsyncAble:

    @abstractmethod
    def do_finish(self, task_log_id: int, response, header: dict, ficus_param: dict, task_status: int) -> ResultVO:
        pass

    @abstractmethod
    def transform_response(self, response, headers: dict) -> AsyncServiceResponse:
        pass