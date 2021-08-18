
from assembly_payments.services.base import BaseService
from assembly_payments.types import Callback, CallbackRequest, CallbackUpdateRequest


class CallbackService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/callbacks"

    def get(self, callback_id):
        response = self._execute(CallbackService.GET, f"{self.endpoint}/{callback_id}")
        return Callback(**response)

    def list(self, *args, **kwargs):
        response = self._execute(CallbackService.GET, self.endpoint)
        return list(map(lambda x: Callback(**x), response.get("callbacks", [])))

    def create(self, **kwargs):
        data = CallbackRequest(**kwargs)
        response = self._execute(CallbackService.POST, self.endpoint, data=data.dict(exclude_none=True))
        return Callback(**response)

    def update(self, callback_id, **kwargs):
        data = CallbackUpdateRequest(**kwargs)
        response = self._execute(CallbackService.PATCH, f"{self.endpoint}/{callback_id}", data=data.dict(exclude_none=True))
        return Callback(**response['callbacks'])

    def delete(self, callback_id):
        self._execute(CallbackService.DELETE, f"{self.endpoint}/{callback_id}")
