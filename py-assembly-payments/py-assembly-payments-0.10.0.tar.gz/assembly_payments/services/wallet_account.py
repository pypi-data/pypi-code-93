from assembly_payments.services.base import BaseService
from assembly_payments.types import (
    User,
    WalletAccount,
    NppDetails,
    BpayDetails,
    VirtualAccount,
    Disbursement,
    WithdrawFundsRequest,
)


class WalletAccountService(BaseService):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = "/wallet_accounts"

    def get(self, wallet_account_id):
        response = self._execute(
            WalletAccountService.GET, f"{self.endpoint}/{wallet_account_id}"
        )
        return WalletAccount(**response["wallet_accounts"])

    def get_user(self, wallet_account_id):
        response = self._execute(
            WalletAccountService.GET, f"{self.endpoint}/{wallet_account_id}/users"
        )
        return User(**response["users"])

    def get_wallet_account_npp_details(self, wallet_account_id):
        response = self._execute(
            WalletAccountService.GET, f"{self.endpoint}/{wallet_account_id}/npp_details"
        )
        return NppDetails(**response["wallet_accounts"]["npp_details"])

    def get_wallet_account_bpay_details(self, wallet_account_id):
        response = self._execute(
            WalletAccountService.GET,
            f"{self.endpoint}/{wallet_account_id}/bpay_details",
        )
        return BpayDetails(**response["wallet_accounts"]["bpay_details"])

    def get_virtual_accounts(self, wallet_account_id):
        response = self._execute(
            WalletAccountService.GET,
            f"{self.endpoint}/{wallet_account_id}/virtual_accounts",
            url=self.beta_url,
        )
        return list(map(lambda x: VirtualAccount(**x), response.get("virtual_accounts", [])))

    def withdraw_funds(self, wallet_account_id, **kwargs):
        data = WithdrawFundsRequest(**kwargs)
        response = self._execute(
            WalletAccountService.POST,
            f"{self.endpoint}/{wallet_account_id}/withdraw",
            data=data.dict(),
        )
        return Disbursement(**response["disbursements"])
