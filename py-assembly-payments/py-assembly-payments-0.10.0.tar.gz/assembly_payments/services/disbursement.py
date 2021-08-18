
from assembly_payments.services.base import BaseService
from assembly_payments.types import Disbursement, BankAccount, Item, Transaction, User, WalletAccount


class DisbursementService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/disbursements"

    def get(self, disbursement_id):
        response = self._execute(DisbursementService.GET, f"{self.endpoint}/{disbursement_id}")
        return Disbursement(**response['disbursements'])

    def list(self, *args, **kwargs):
        response = self._execute(DisbursementService.GET, self.endpoint)
        return list(map(lambda x: Disbursement(**x), response.get("disbursements", [])))

    def get_user(self, disbursement_id):
        response = self._execute(DisbursementService.GET, f"{self.endpoint}/{disbursement_id}/users")
        return User(**response['users'])

    def get_wallet_account(self, disbursement_id):
        response = self._execute(DisbursementService.GET, f"{self.endpoint}/{disbursement_id}/wallet_accounts")
        return WalletAccount(**response['wallet_accounts'])

    def get_bank_account(self, disbursement_id):
        response = self._execute(DisbursementService.GET, f"{self.endpoint}/{disbursement_id}/bank_accounts")
        return BankAccount(**response['bank_accounts'])

    def get_items(self, disbursement_id):
        response = self._execute(DisbursementService.GET, f"{self.endpoint}/{disbursement_id}/items")
        return list(map(lambda x: Item(**x), response.get("items", [])))

    def get_transactions(self, disbursement_id):
        response = self._execute(DisbursementService.GET, f"{self.endpoint}/{disbursement_id}/transactions")
        return list(map(lambda x: Transaction(**x), response.get("transactions", [])))