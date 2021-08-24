import os
import json

from neon_api_proxy.owm_api import OpenWeatherAPI
from neon_api_proxy.alpha_vantage_api import AlphaVantageAPI
from neon_api_proxy.wolfram_api import WolframAPI
from neon_api_proxy.test_api import TestAPI


class NeonAPIProxyController:
    """
        Generic module for binding between service name and actual service for fulfilling request
    """

    # Mapping between string service name and actual class
    service_class_mapping = {
        'wolfram_alpha': WolframAPI,
        'alpha_vantage': AlphaVantageAPI,
        'open_weather_map': OpenWeatherAPI,
        'api_test_endpoint': TestAPI
    }

    def __init__(self, config: dict = None):
        """
            @param config: configurations dictionary
        """
        self.config = config
        self.service_instance_mapping = self.init_service_instances(self.service_class_mapping)

    def init_service_instances(self, service_class_mapping: dict) -> dict:
        """
            Maps service classes to their instances
            @param service_class_mapping: dictionary containing mapping between service string name
                    and python class representing it

            @return dictionary containing mapping between service string name
                    and instance of python class representing it
        """
        service_mapping = dict()
        for item in list(service_class_mapping):
            api_key = self.config.get("SERVICES", {}).get(item, {}).get("api_key") if self.config else None
            service_mapping[item] = service_class_mapping[item](api_key=api_key)
        return service_mapping

    def resolve_query(self, query: dict) -> dict:
        """
            Generically resolves input query dictionary by mapping its "service" parameter
            @param query: dictionary with query parameters
            @return: response from the destination service
        """
        target_service = query.get('service', None)
        message_id = query.pop('message_id', None)
        if target_service and target_service in list(self.service_instance_mapping):
            resp = self.service_instance_mapping[target_service].handle_query(**query)
        else:
            resp = {
                "status_code": 401,
                "content": f"Unresolved service name: {target_service}",
                "encoding": "utf-8"
            }
        resp['message_id'] = message_id
        return resp
