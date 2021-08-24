from market_place_cli.v_cloud_market_cli_common.utils.server_api_wrapper import NewServerWrapper
from market_place_cli.v_cloud_market_cli_common.config.server_config import API_VERSION
from market_place_cli.v_cloud_market_cli_common.service.service_common import ServiceCommon

class UserServiceQueryParam:
    service_active = True
    service_id = ''
    service = ''
    status = []
    start_from = 0
    end_at = 0
    current = 1
    page_size = 10

    def as_dict(self) -> dict:

        return {
            'serviceActivated': self.service_active,
            'serviceID': self.service_id,
            'service': self.service,
            'serviceStatuses[]': self.status,
            'userServiceStartFrom': self.start_from,
            'userServiceEndAt': self.end_at,
            'current': self.current,
            'pageSize': self.page_size
        }


class UserService:

    def __init__(self, net_type: str, password: str, nonce=0):
        self.cli, _ = NewServerWrapper(net_type, password, nonce)

    def get_user_service_page(self, current=1, page_size=10, statuses=None):
        '''
        Query user service via order info
        '''
        orderRoute = API_VERSION + '/order'

        activated = True
        if type(statuses) is not list:
            activated = statuses in ['ServicePending', 'ServiceRunning']
        opts = {
            'current': current,
            'pageSize': page_size,
            'serviceActivated': activated,
            'serviceStatuses[]': statuses if type(statuses) is list else [statuses]
        }

        opts = {k: v for k, v in opts.items() if v is not None}
        resp = self.cli.get_request(orderRoute, url_param=opts)
        ServiceCommon.validate_response(resp)
        return resp

    def get_user_service_info(self, provider_host: str, user_service_id: str):
        route = API_VERSION + '/userService/' + user_service_id
        tmp = self.cli.node_host
        self.cli.node_host = provider_host
        resp = self.cli.get_request(route, needAuth=True)
        ServiceCommon.validate_response(resp)
        self.cli.node_host = tmp
        return resp

    def access_user_api_get(self, user_service_id: str, api_type: str, api_func: str):
        route = API_VERSION + f'/service/userAPI/get/{api_type}/{api_func}/{user_service_id}'
        resp = self.cli.get_request(route, needAuth=True)
        return resp

    def access_user_api_post(self, user_service_id: str, api_type: str, api_func: str):
        pass

    def query_user_service(self, param: UserServiceQueryParam):
        route = API_VERSION + '/order'
        resp = self.cli.get_request(route, url_param=param.as_dict())
        ServiceCommon.validate_response(resp)
        return resp

    def _get_service_provider_api(self, provider_id: str):
        route = API_VERSION + '/service/provider/' + provider_id
        resp = self.cli.get_request(route)

        if isinstance(resp, dict):
            result = {
                'provider': resp.get('name', ''),
                'apiHost': resp.get('apiHost', '')
            }
        else:
            result = {
                'provider': '',
                'apiHost': ''
            }
        return result

    def _get_order_distinct_list(self, distinct_field: str, order_statuses: list):
        '''
        return: a list of distinct_field value
        '''
        route = API_VERSION + '/order/distinct'
        opts = {
            'distinctField': distinct_field,
            'statuses': order_statuses if type(order_statuses) is list else [order_statuses]
        }
        resp = self.cli.get_request(route, url_param=opts)
        ServiceCommon.validate_response(resp)
        return resp
