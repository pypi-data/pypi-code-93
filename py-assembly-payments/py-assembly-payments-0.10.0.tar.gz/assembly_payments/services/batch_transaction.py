
from assembly_payments.services.base import BaseService
from assembly_payments.types import BatchTransaction


class BatchTransactionService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/batch_transactions"

    def get(self, transaction_id):
        response = self._execute(
            BatchTransactionService.GET, f"{self.endpoint}/{transaction_id}"
        )
        return BatchTransaction(**response)

    def list(self):
        response = self._execute(BatchTransactionService.GET, f"{self.endpoint}")
        return list(map(lambda x: BatchTransaction(**x), response.get("batch_transactions", [])))