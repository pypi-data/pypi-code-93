import sys
from typing import Callable

import click
from ledgerwallet import __version__ as ledger_wallet_version
from ledgerwallet import utils
from ledgerwallet.client import CommException, LedgerClient
from ledgerwallet.transport import enumerate_devices
from stellar_sdk import Network, parse_transaction_envelope_from_xdr

from strledger import __issue__
from strledger import __version__ as strledger_version
from strledger.core import SW, StrLedger

_DEFAULT_KEYPAIR_INDEX = 0


def echo_normal(message: str) -> None:
    click.echo(message)


def echo_success(message: str) -> None:
    click.echo(click.style(message, fg="green"))


def echo_error(message: str) -> None:
    click.echo(click.style(message, fg="red"))


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Display exchanged APDU.")
@click.pass_context
def cli(ctx, verbose):
    """Stellar Ledger commands.

    This project is built on the basis of ledgerctl,
    you can check ledgerctl for more features.
    """

    if verbose:
        utils.enable_apdu_log()

    def get_client() -> StrLedger:
        devices = enumerate_devices()
        if len(devices) == 0:
            echo_error("No Ledger device has been found.")
            sys.exit(0)
        client = LedgerClient(devices[0])
        return StrLedger(client)

    ctx.obj = get_client


@cli.command(name="app-config")
@click.pass_obj
def get_app_config(get_client: Callable[[], StrLedger]) -> None:
    """Get Stellar app config."""
    client = get_client()
    data = client.get_app_configuration()
    echo_success(f"Stellar App Version: {data.version}")
    enabled = "Yes" if data.hash_signing_enabled else "No"
    echo_success(f"Hash Signing Enabled: {enabled}")


@cli.command(name="sign-tx")
@click.option(
    "-n",
    "--network-passphrase",
    default=Network.PUBLIC_NETWORK_PASSPHRASE,
    required=False,
    help="Network passphrase (blank for public network).",
)
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=_DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.argument("transaction_envelope")
@click.pass_obj
def sign_transaction(
    get_client: Callable[[], StrLedger],
    network_passphrase: str,
    transaction_envelope: str,
    keypair_index: int,
):
    """Sign a base64-encoded transaction envelope.

    For testnet transactions, use the following network passphrase:
    'Test SDF Network ; September 2015'
    """
    client = get_client()
    echo_normal(f"Network Passphrase: {network_passphrase}")
    echo_normal("Please confirm this transaction on Ledger.")
    try:
        te = parse_transaction_envelope_from_xdr(
            xdr=transaction_envelope, network_passphrase=network_passphrase
        )
    except Exception:
        echo_error(
            "Failed to parse XDR.\n"
            "Make sure to pass a valid base64-encoded transaction envelope.\n"
            "You can check whether the data you submitted is valid "
            "through XDR Viewer - https://laboratory.stellar.org/#xdr-viewer"
        )
        sys.exit(1)

    try:
        client.sign_transaction(transaction_envelope=te, keypair_index=keypair_index)
    except CommException as e:
        if e.sw == SW.CANCEL:
            echo_error("Transaction approval request was rejected.")
        elif e.sw == SW.UNKNOWN_OP:
            echo_error("The transaction contains unsupported operation(s).")
        else:
            echo_error(f"Unknown exception, you can the problem here: {__issue__}")
            raise
        sys.exit(1)
    echo_success("Signed successfully. Base64-encoded signed transaction envelope:")
    echo_success(te.to_xdr())


@cli.command(name="get-address")
@click.option(
    "-i",
    "--keypair-index",
    type=int,
    required=False,
    help="Keypair Index.",
    default=_DEFAULT_KEYPAIR_INDEX,
    show_default=True,
)
@click.pass_obj
def get_address(get_client: Callable[[], StrLedger], keypair_index: int) -> None:
    """Get Stellar public address."""
    client = get_client()
    keypair = client.get_keypair(keypair_index)
    echo_success(keypair.public_key)


@cli.command(name="version")
def version() -> None:
    """Get version info."""
    echo_success(f"StrLedger Version: {strledger_version}")
    echo_success(f"Ledger Wallet Version: {ledger_wallet_version}")


if __name__ == "__main__":
    cli()
