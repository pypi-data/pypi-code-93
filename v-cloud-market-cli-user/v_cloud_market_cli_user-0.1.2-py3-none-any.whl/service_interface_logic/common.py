from market_place_cli.v_cloud_market_cli_common.service.wallet_service import WalletService
from market_place_cli.v_cloud_market_cli_common.utils.service_error import WalletStorageLoadingException


def get_net(is_testnet) -> str:
    return 'T' if is_testnet else 'M'


def wallet_has_password(net_type: str) -> bool:
    try:
        WalletService(None, net_type, "")
        return False
    except WalletStorageLoadingException:
        return True
