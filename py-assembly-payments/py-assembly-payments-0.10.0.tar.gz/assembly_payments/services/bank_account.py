
from assembly_payments.services.base import BaseService
from assembly_payments.types import BankAccount, User, BankAccountRequest


class BankAccountService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/bank_accounts"

    def get(self, bank_account_id):
        response = self._execute(BankAccountService.GET, f"{self.endpoint}/{bank_account_id}")
        return BankAccount(**response['bank_accounts'])

    def get_user(self, bank_account_id):
        response = self._execute(BankAccountService.GET, f"{self.endpoint}/{bank_account_id}/users")
        return User(**response['users'])

    def create(self, **kwargs):
        data = BankAccountRequest(**kwargs)
        response = self._execute(BankAccountService.POST, self.endpoint, data=data.dict())
        return BankAccount(**response['bank_accounts'])

    def delete(self, bank_account_id):
        self._execute(BankAccountService.DELETE, f"{self.endpoint}/{bank_account_id}")
