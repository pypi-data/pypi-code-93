import os
from datetime import datetime

from assembly_payments.services.bank_account import BankAccountService
from assembly_payments.services.batch_transaction import BatchTransactionService
from assembly_payments.services.callback import CallbackService
from assembly_payments.services.company import CompanyService
from assembly_payments.services.direct_debit_authority import (
    DirectDebitAuthorityService,
)
from assembly_payments.services.disbursement import DisbursementService
from assembly_payments.services.item import ItemService
from assembly_payments.services.testing import TestingService
from assembly_payments.services.token import TokenService
from assembly_payments.services.user import UserService
from assembly_payments.services.virtual_account import VirtualAccountService
from assembly_payments.services.wallet_account import WalletAccountService
from assembly_payments.services.webhook import WebhookService

PROD_BASE_URL = "https://secure.api.promisepay.com"
PROD_AUTH_URL = "https://au-0000.auth.assemblypay.com"
PROD_BETA_URL = "https://au-0000.api.assemblypay.com"
TEST_BASE_URL = "https://test.api.promisepay.com"
TEST_AUTH_URL = "https://au-0000.sandbox.auth.assemblypay.com"
TEST_BETA_URL = "https://sandbox.au-0000.api.assemblypay.com"


class AssemblyClient:
    def __init__(
        self,
        client_id=None,
        client_secret=None,
        scope=None,
        grant_type=None,
        use_production=False,
        logging=False,
    ):
        self.client_id = client_id or os.environ.get("ASSEMBLY_CLIENT_ID", None)
        self.client_secret = client_secret or os.environ.get(
            "ASSEMBLY_CLIENT_SECRET", None
        )
        self.scope = scope or os.environ.get("ASSEMBLY_SCOPE", None)
        self.grant_type = grant_type or "client_credentials"
        self.logging = logging
        self.token = None

        self.base_url = TEST_BASE_URL
        self.auth_url = TEST_AUTH_URL
        self.beta_url = TEST_BETA_URL
        if use_production:
            self.base_url = PROD_BASE_URL
            self.auth_url = PROD_AUTH_URL
            self.beta_url = PROD_BETA_URL

        self._initialise_services()

    def get_auth(self):
        def refresh_token():
            return TokenService(
                base_url=self.base_url, auth_url=self.auth_url, logging=self.logging
            ).create(
                grant_type=self.grant_type,
                client_id=self.client_id,
                client_secret=self.client_secret,
                scope=self.scope,
            )

        if not self.token or self.token.expires_at <= datetime.now().timestamp():
            self.token = refresh_token()
        return self.token.access_token

    def _initialise_services(self):
        kwargs = dict(
            base_url=self.base_url,
            auth_url=self.auth_url,
            beta_url=self.beta_url,
            get_auth=self.get_auth,
            logging=self.logging,
        )
        self.users = UserService(**kwargs)
        self.companies = CompanyService(**kwargs)
        self.wallet_accounts = WalletAccountService(**kwargs)
        self.virtual_accounts = VirtualAccountService(**kwargs)
        self.bank_accounts = BankAccountService(**kwargs)
        self.disbursements = DisbursementService(**kwargs)
        self.items = ItemService(**kwargs)
        self.webhooks = WebhookService(**kwargs)
        self.direct_debit_authority = DirectDebitAuthorityService(**kwargs)
        self.testing = TestingService(**kwargs)
        self.callbacks = CallbackService(**kwargs)
        self.batch_transactions = BatchTransactionService(**kwargs)
