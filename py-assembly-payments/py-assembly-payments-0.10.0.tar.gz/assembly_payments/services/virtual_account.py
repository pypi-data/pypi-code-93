
from assembly_payments.services.base import BaseService
from assembly_payments.types import VirtualAccount


class VirtualAccountService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/virtual_accounts"

    def get(self, virtual_account_id):
        response = self._execute(VirtualAccountService.GET, f"{self.endpoint}/{virtual_account_id}", url=self.beta_url)
        return VirtualAccount(**response)

    def create(self, wallet_account_id):
        response = self._execute(VirtualAccountService.POST, f"/wallet_accounts/{wallet_account_id}/virtual_accounts", url=self.beta_url)
        return VirtualAccount(**response)
