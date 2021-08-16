from dataclasses import dataclass


@dataclass
class PlaceOrderResponse(object):

    status: str
    desc: str
    order_id: str
    client_order_id: str


@dataclass
class QueryBalanceResponse(object):

    status: str
    desc: str


@dataclass
class QueryOrderResponse(object):

    status: str
    desc: str
    order_id: str
    client_order_id: str
    amount: str
    mobile: str
    charge_time: str


@dataclass
class QueryPointsResponse(object):

    status: str
    desc: str
