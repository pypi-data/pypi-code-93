from assembly_payments.services.base import BaseService
from assembly_payments.types import (
    BankAccount,
    User,
    BankAccountRequest,
    ProcessNppPaymentRequest,
    TransactionStatesRequest, UserRequest,
)


class TestingService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/testing"

    def process_npp_payment(self, **kwargs):
        data = ProcessNppPaymentRequest(**kwargs)
        response = self._execute(
            TestingService.PATCH,
            f"{self.endpoint}/wallet_accounts/process_npp_payin",
            data=data.dict(),
        )
        return response

    def move_pending_batch_transactions_to_batched(self):
        response = self._execute(
            TestingService.GET, f"/batch_transactions/export_transactions"
        )
        return response

    def update_batched_transaction_state(self, id, state):
        data = TransactionStatesRequest(exported_ids=[id], state=state)
        response = self._execute(
            TestingService.PATCH, f"/batches/{id}/transaction_states", data=data.dict()
        )
        return response

    def verify_user(self, user_id):
        return self._execute(
            TestingService.PATCH, f"/users/{user_id}/identity_verified"
        )
