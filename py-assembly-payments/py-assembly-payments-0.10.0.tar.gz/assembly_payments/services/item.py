
from assembly_payments.services.base import BaseService
from assembly_payments.types import Item, User, ItemRequest, MakePaymentRequest, RefundPaymentRequest, \
    AuthorizePaymentRequest


class ItemService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/items"

    def get(self, item_id):
        response = self._execute(ItemService.GET, f"{self.endpoint}/{item_id}")
        return Item(**response['items'])

    def list(self, *args, **kwargs):
        response = self._execute(ItemService.GET, self.endpoint)
        return list(map(lambda x: Item(**x), response.get("items", [])))

    def get_seller(self, item_id):
        response = self._execute(ItemService.GET, f"{self.endpoint}/{item_id}/sellers")
        return User(**response['users'])

    def get_buyer(self, item_id):
        response = self._execute(ItemService.GET, f"{self.endpoint}/{item_id}/buyers")
        return User(**response['users'])

    def create(self, **kwargs):
        data = ItemRequest(**kwargs)
        response = self._execute(ItemService.POST, self.endpoint, data=data.dict())
        return Item(**response['items'])

    def make_payment(self, item_id, **kwargs):
        data = MakePaymentRequest(**kwargs)
        response = self._execute(ItemService.PATCH, f"{self.endpoint}/{item_id}/make_payment", data=data.dict())
        return Item(**response['items'])

    def cancel_payment(self, item_id):
        response = self._execute(ItemService.PATCH, f"{self.endpoint}/{item_id}/cancel")
        return Item(**response['items'])

    def refund_payment(self, item_id, **kwargs):
        data = RefundPaymentRequest(**kwargs)
        response = self._execute(ItemService.PATCH, f"{self.endpoint}/{item_id}/refund", data=data.dict(exclude_unset=True))
        return Item(**response['items'])

    def authorize_payment(self, item_id, **kwargs):
        data = AuthorizePaymentRequest(**kwargs)
        response = self._execute(ItemService.PATCH, f"{self.endpoint}/{item_id}/authorize_payment", data=data.dict(exclude_unset=True))
        return Item(**response['items'])

    def capture_payment(self, item_id):
        response = self._execute(ItemService.PATCH, f"{self.endpoint}/{item_id}/capture_payment")
        return Item(**response['items'])

    def void_payment(self, item_id):
        response = self._execute(ItemService.PATCH, f"{self.endpoint}/{item_id}/void_payment")
        return Item(**response['items'])
