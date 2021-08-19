from .connection import Connection

from logging import getLogger, NullHandler
logger = getLogger(__name__)
logger.addHandler(NullHandler())


class PrivateClient:
    def __init__(self, apikey, apisecret):
        self.connection = Connection(apikey, apisecret)

    def permissions(self):
        return self.connection.get('/v1/me/getpermissions')

    def balance(self):
        return self.connection.get('/v1/me/getbalance')

    def collateral(self):
        return self.connection.get('/v1/me/getcollateral')

    def addresses(self):
        return self.connection.get('/v1/me/getaddresses')

    def coin_ins(self):
        return self.connection.get('/v1/me/getcoinins')

    def coin_outs(self):
        return self.connection.get('/v1/me/getcoinouts')

    def bank_accounts(self):
        return self.connection.get('/v1/me/getbankaccounts')

    def deposits(self):
        return self.connection.get('/v1/me/getdeposits')

    def withdraw(self, currency_code='JPY', bank_account_id=None, amount=None, code=None):
        body = dict(
            currency_code=currency_code,
            bank_account_id=bank_account_id,
            amount=amount,
            code=code,
        )
        body = {k: v for k, v in body.items() if v is not None}
        self.connection.post('/v1/me/withdraw', body)

    def withdrawals(self):
        self.connection.get('/v1/me/getwithdrawals')

    def send_child_order(
        self,
        product_code='BTC_JPY',
        child_order_type=None,
        side=None,
        price=None,
        size=None,
        minute_to_expire=None,
        time_in_force='GTC',
    ):
        body = dict(
            product_code=product_code,
            child_order_type=child_order_type,
            side=side,
            price=price,
            size=size,
            minute_to_expire=minute_to_expire,
            time_in_force=time_in_force,
        )
        body = {k: v for k, v in body.items() if v is not None}
        return self.connection.post('/v1/me/sendchildorder', body)

    def cancel_child_order(self, product_code='BTC_JPY', child_order_id=None, child_order_acceptance_id=None):
        body = dict(
            product_code=product_code,
            child_order_id=child_order_id,
            child_order_acceptance_id=child_order_acceptance_id,
        )
        body = {k: v for k, v in body.items() if v is not None}
        return self.connection.post('/v1/me/cancelchildorder', body)

    def send_parent_order(self, order_method=None, minute_to_expire=None, time_in_force='GTC', parameters={}):
        body = dict(
            order_method=order_method,
            minute_to_expire=minute_to_expire,
            time_in_force=time_in_force,
            parameters=parameters,
        )
        body = {k: v for k, v in body.items() if v is not None}
        return self.connection.post('/v1/me/sendparentorder', body)

    def cancel_parent_order(self, product_code='BTC_JPY', parent_order_id=None, parent_order_acceptance_id=None):
        body = dict(
            product_code=product_code,
            parent_order_id=parent_order_id,
            parent_order_acceptance_id=parent_order_acceptance_id,
        )
        body = {k: v for k, v in body.items() if v is not None}
        return self.connection.post('/v1/me/cancelparentorder', body)

    def cancel_all_child_orders(self, product_code='BTC_JPY'):
        return self.connection.post('/v1/me/cancelallchildorders', product_code=product_code)

    def child_orders(
        self,
        product_code='BTC_JPY',
        count=None,
        before=None,
        after=None,
        child_order_state=None,
        parent_order_id=None,
    ):
        query = dict(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
            child_order_state=child_order_state,
            parent_order_id=parent_order_id,
        )
        query = {k: v for k, v in query.items() if v is not None}
        return self.connection.get('/v1/me/getchildorders', query)

    def parent_orders(self, product_code='BTC_JPY', count=None, before=None, after=None, parent_order_state=None):
        query = dict(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
            parent_order_state=parent_order_state,
        )
        query = {k: v for k, v in query.items() if v is not None}
        return self.connection.get('/v1/me/getparentorders', query)

    def parent_order(self, parent_order_id=None, parent_order_acceptance_id=None):
        query = dict(
            parent_order_id=parent_order_id,
            parent_order_acceptance_id=parent_order_acceptance_id,
        )
        query = {k: v for k, v in query.items() if v is not None}
        return self.connection.get('/v1/me/getparentorder', query)

    def executions(
        self,
        product_code='BTC_JPY',
        count=None,
        before=None,
        after=None,
        child_order_id=None,
        child_order_acceptance_id=None,
    ):
        query = dict(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
            child_order_id=child_order_id,
            child_order_acceptance_id=child_order_acceptance_id,
        )
        query = {k: v for k, v in query.items() if v is not None}
        return self.connection.get('/v1/me/getexecutions', query)

    def balance_history(self, currency_code=None, count=None, before=None, after=None):
        query = dict(
            currency_code=currency_code,
            count=count,
            before=before,
            after=after
        )
        query = {k: v for k, v in query.items() if v is not None}
        return self.connection.get('/v1/me/getbalancehistory', query)

    def positions(self, product_code='FX_BTC_JPY'):
        return self.connection.get('/v1/me/getpositions', product_code=product_code)

    def trading_commission(self, product_code='BTC_JPY'):
        return self.connection.get('v1/me/gettradingcommission', product_code=product_code)
