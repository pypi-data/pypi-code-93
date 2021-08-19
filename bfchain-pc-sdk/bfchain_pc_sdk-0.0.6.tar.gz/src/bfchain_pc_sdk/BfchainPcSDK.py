# -*- coding: utf-8 -*-

from core.basic_api import (
    get_bf_chain_version as basic_get_bf_chain_version,
    get_last_block as basic_get_last_block,
    get_block as basic_get_block,
    get_transactions as basic_get_transactions,
    get_account_last_transaction as basic_get_account_last_transaction,
    create_account as basic_create_account,
    get_block_chain_status as basic_get_block_chain_status,
    get_account_last_type_transaction as basic_get_account_last_type_transaction,
)
from core.event_api import (
    tr_dapp as event_tr_dapp,
    dapp as event_dapp,
    tr_dapp_purchasing as event_tr_dapp_purchasing,
    dapp_purchasing as event_dapp_purchasing

)

from src.bfchain_pc_sdk.util.helper import (
    signature_message
)


class BfchainPcSDK(object):
    def __init__(self, config=dict()):
        if config.has_key('base_url'):
            self.base_url = config['base_url']

    def get_bf_chain_version(self):
        """
        获得Bfchain版本号
        :return:
        """
        return basic_get_bf_chain_version(self.base_url)

    def get_last_block(self):
        """
        获取本地节点当前最新区块
        :return:
        """
        return basic_get_last_block(self.base_url)

    def get_block(self, data):
        """
        获取指定区块
        :param data:
        :return:
        """
        return basic_get_block(self.base_url, data)

    def get_transactions(self, data):
        """
        获取指定事件
        :param data:
        :return:
        """
        return basic_get_transactions(self.base_url, data)

    def get_account_last_transaction(self, data):
        """
        获取账户的最后一笔交易
        :param data:
        :return:
        """
        return basic_get_account_last_transaction(self.base_url, data)

    def create_account(self, data):
        """
        创建账户
        :param data:
        :return:
        """
        return basic_create_account(self.base_url, data)

    def get_block_chain_status(self, data):
        """
        获取节点状态
        :param data:
        :return:
        """
        return basic_get_block_chain_status(self.base_url, data)

    def get_account_last_type_transaction(self, data):
        """
        根据交易类型获取账户的最后一笔交易
        :param data:
        :return:
        """
        return basic_get_account_last_type_transaction(self.base_url, data)

    def dapp(self, data, sk, with_sign=False):
        """
        发行dapp事件
        :param data:
        :param sk:
        :param with_sign:
        :return:
        """
        create_res = event_tr_dapp(self.base_url, data)
        if 'buffer' not in create_res:
            raise IOError("创建dapp事件失败")
        buf = str(create_res['buffer'])
        b, s = signature_message(buf, sk)
        if with_sign:
            return None
        else:
            data = {'buffer': b, 'signature': s}
            return event_dapp(self.base_url, data)

    def dapp_purchasing(self, data, sk, with_sign=False):
        """
        dapp购买事件
        :param data:
        :param sk:
        :param with_sign:
        :return:
        """
        create_res = event_tr_dapp_purchasing(self.base_url, data)
        if 'buffer' not in create_res:
            raise IOError("创建dapp购买事件失败")
        buf = str(create_res['buffer'])
        b, s = signature_message(buf, sk)
        if with_sign:
            return None
        else:
            data = {'buffer': b, 'signature': s}
            return event_dapp_purchasing(self.base_url, data)

    def check_dapp_purchase_status(self,dapp_id,address,min_height):
        """
        检查指定地址是否有购买对应的dapp
        :param dapp_id:
        :param address:
        :param min_height:
        :return:
        """
        data = {"senderId": address, "storageKey":"dappid","storageValue": dapp_id, "minHeight": min_height,'type':["BFT-BFCHAIN-WOD-01"]}
        res = basic_get_transactions(self.base_url, data)
        if 'count' in res:
            return True if res['count'] > 0 else False
        return False
