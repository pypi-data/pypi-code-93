import base64
import hashlib
import json
import requests
import ecdsa

import cyberpy.interfaces.tx_pb2 as tx
import cyberpy.interfaces.msg_send_pb2 as transfer
import cyberpy.interfaces.coin_pb2 as coin
import cyberpy.interfaces.pubkey_pb2 as pubkey
import cyberpy.interfaces.msg_link_pb2 as MsgCyberlink

from cyberpy.interfaces.any_pb2 import Any
from cyberpy._wallet import privkey_to_address, privkey_to_pubkey
from cyberpy._typing import SyncMode


class Transaction:
    """A Cyber transaction.

    After initialization, one or more messages can be added by
    calling the `add_transfer()`, `add_cyberlink` method. Then, call `get_pushable()`
    to get a signed transaction that can be pushed to the `POST /txs`
    endpoint of the Cyber gRPC or call `broadcast(url=<gRPC_api>)` method
    to get signed transaction and broadcast it with gRPC_API.
    """

    def __init__(
        self,
        *,
        privkey: bytes,
        account_num: int,
        sequence: int,
        fee: int,
        gas: int,
        fee_denom: str = "boot",
        memo: str = "",
        chain_id: str = "bostrom-testnet-4",
        sync_mode: SyncMode = "broadcast_tx_commit",
    ) -> None:
        self._raw_tx = tx.TxRaw()
        self._tx_body = tx.TxBody()
        self._tx_body.memo = memo
        self._privkey = privkey
        self._account_num = account_num
        self._sequence = sequence
        self._fee = fee
        self._fee_denom = fee_denom
        self._gas = gas
        self._chain_id = chain_id
        self._sync_mode = sync_mode

    def add_transfer(self, recipient: str, amount: int, denom: str = "boot") -> None:
        msg_send = transfer.MsgSend()
        msg_send.from_address = privkey_to_address(self._privkey)
        msg_send.to_address = recipient
        _amount = coin.Coin()
        _amount.denom = denom
        _amount.amount = str(amount)
        msg_send.amount.append(_amount)
        msg_send_any = Any()
        msg_send_any.Pack(msg_send)
        msg_send_any.type_url = '/cosmos.bank.v1beta1.MsgSend'
        self._tx_body.messages.append(msg_send_any)

    def add_cyberlink(self, cid_from: str, cid_to: str) -> None:
        msg_link = MsgCyberlink.MsgCyberlink()
        msg_link.address = privkey_to_address(self._privkey)
        links = MsgCyberlink.Link()
        links.__setattr__('from', cid_from)
        links.__setattr__('to', cid_to)
        msg_link.links.append(links)
        msg_link_any = Any()
        msg_link_any.Pack(msg_link)
        msg_link_any.type_url = '/cyber.graph.v1beta1.MsgCyberlink'
        self._tx_body.messages.append(msg_link_any)

    def add_chain_cyberlink(self, chainlink: list) -> None:
        msg_link = MsgCyberlink.MsgCyberlink()
        msg_link.address = privkey_to_address(self._privkey)
        for cyberlink in chainlink:
            links = MsgCyberlink.Link()
            links.__setattr__('from', cyberlink[0])
            links.__setattr__('to', cyberlink[1])
            msg_link.links.append(links)
        msg_link_any = Any()
        msg_link_any.Pack(msg_link)
        msg_link_any.type_url = '/cyber.graph.v1beta1.MsgCyberlink'
        self._tx_body.messages.append(msg_link_any)

    def get_pushable(self):
        self._raw_tx.body_bytes = self._tx_body.SerializeToString()
        self._raw_tx.auth_info_bytes = self._get_auth_info().SerializeToString()
        self._raw_tx.signatures.append(self._get_signatures())
        raw_tx = self._raw_tx.SerializeToString()
        tx_bytes = bytes(raw_tx)
        tx_b64 = base64.b64encode(tx_bytes).decode('utf-8')
        return json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": self._sync_mode,
            "params": {
                "tx": tx_b64
                }
        })

    def _get_signatures(self):
        privkey = ecdsa.SigningKey.from_string(self._privkey, curve=ecdsa.SECP256k1)
        signature_compact = privkey.sign_deterministic(
            self._get_sign_doc().SerializeToString(), hashfunc=hashlib.sha256, sigencode=ecdsa.util.sigencode_string_canonize
        )
        return signature_compact

    def _get_sign_doc(self):
        sign_doc = tx.SignDoc()
        sign_doc.body_bytes = self._tx_body.SerializeToString()
        sign_doc.auth_info_bytes = self._get_auth_info().SerializeToString()
        sign_doc.chain_id = self._chain_id
        sign_doc.account_number = self._account_num
        return sign_doc

    def _get_auth_info(self):
        _auth_info = tx.AuthInfo()
        _auth_info.signer_infos.append(self._get_signer_infos(self._get_pubkey()))
        _auth_info.fee.gas_limit = self._gas
        _auth_info.fee.amount.append(self._get_fee())
        return _auth_info

    def _get_fee(self):
        _fee = coin.Coin()
        _fee.amount = str(self._fee)
        _fee.denom = self._fee_denom
        return _fee

    def _get_pubkey(self):
        pubkey_bytes = privkey_to_pubkey(self._privkey)
        _pubkey = pubkey.PubKey()
        _pubkey.key = pubkey_bytes
        return _pubkey

    def _get_signer_infos(self, _pubkey):
        signer_infos = tx.SignerInfo()
        signer_infos.sequence = self._sequence
        signer_infos.public_key.Pack(_pubkey)
        signer_infos.public_key.type_url = '/cosmos.crypto.secp256k1.PubKey'
        signer_infos.mode_info.single.mode = 1
        return signer_infos

    def broadcast(self, url):
        pushable_tx = self.get_pushable()
        res = requests.post(url=url, data=pushable_tx)
        if res.status_code == 200:
            res = res.json()
            return res
        else:
            raise Exception("Broadcact failed to run by returning code of {}".format(res.status_code))
