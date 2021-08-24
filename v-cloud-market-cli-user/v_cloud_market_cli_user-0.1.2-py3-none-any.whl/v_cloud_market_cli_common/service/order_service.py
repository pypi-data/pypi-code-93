from market_place_cli.v_cloud_market_cli_common.utils.server_api_wrapper import NewServerWrapper
from market_place_cli.v_cloud_market_cli_common.config.server_config import API_VERSION, MOCK_PAYMENT_SERVER
from market_place_cli.v_cloud_market_cli_common.service.service_common import ServiceCommon


class OrderQueryParam:
    id = ''
    start_from = 0
    end_at = 0
    service_id = ''
    service = ''
    recipient = ''
    statuses = []
    service_activated = False
    current = 1
    page_size = 10

    def as_dict(self) -> dict:
        return {
            'id': self.id,
            'startFrom': self.start_from,
            'serviceID': self.service_id,
            'service': self.service,
            'recipient': self.recipient,
            'statuses[]': self.statuses,
            'serviceActivated': self.service_activated,
            'current': self.current,
            'pageSize': self.page_size
        }


class OrderService:

    def __init__(self, net_type: str, password: str, nonce=0):
        self.cli, self.account = NewServerWrapper(net_type, password, nonce)

    def get_order_info_page(self, current=1, page_size=10, status='OrderPending'):
        orderRoute = API_VERSION + '/order'
        opts = {
            'current': current,
            'pageSize': page_size,
            'statuses[]': [status]
        }

        if status in ['OrderPaid', 'OrderFiled']:
            opts['serviceActivated'] = True

        opts = {k: v for k, v in opts.items() if v is not None}
        resp = self.cli.get_request(orderRoute, url_param=opts)
        ServiceCommon.validate_response(resp)
        return resp

    def query_order_info(self, params: OrderQueryParam):
        orderRoute = API_VERSION + '/order'
        resp = self.cli.get_request(orderRoute, url_param=params.as_dict())
        ServiceCommon.validate_response(resp)
        return resp

    def get_order_info(self, order_id: str):
        """
        return:
        {
            "createdAt"
            "updatedAt"
            "duration"
            "serviceExpiredDate"
            "amount"
            "amountPaid"
            "serviceID"
            "service"
            "address"
            "recipient"
            "id"
            "serviceOptions"
            "status"
            "publicKey"
        }
        """
        route = API_VERSION + '/order/id/' + order_id
        resp = self.cli.get_request(route, needAuth=True)
        ServiceCommon.validate_response(resp)
        return resp
    
    def refund_order(self, provider_host: str, order_id: str):
        route = API_VERSION + '/order/userRefund/' + order_id
        tmp = self.cli.node_host
        self.cli.node_host = provider_host
        resp = self.cli.post_request(route, needAuth=True)
        ServiceCommon.validate_response(resp)
        self.cli.node_host = tmp
        return resp

    def mock_order_payment(self, order_id: str, provider_addr: str, pub_key: str, amt: int):
        route = API_VERSION + '/order/mock'
        order_mock_payload = {
            'orderId': order_id,
            'providerAddr': provider_addr,
            'pubKey': pub_key,
            'amt': amt * 10**8
        }
        node_host = self.cli.node_host
        self.cli.node_host = MOCK_PAYMENT_SERVER
        resp = self.cli.post_request(route, body_data=order_mock_payload)
        self.cli.node_host = node_host
        ServiceCommon.validate_response(resp)
        return resp
