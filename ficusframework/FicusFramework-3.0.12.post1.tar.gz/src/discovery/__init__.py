import atexit
import logging
import random
from time import sleep
from urllib.error import URLError, HTTPError

import requests
import consul
from munch import Munch

from config.annotation import Value
from libs.utils import Singleton
from py_eureka_client import eureka_client

from api.exceptions import ServiceNoInstanceException, IllegalArgumentException

_logger = logging.getLogger('FICUS')


class DiscoveryServiceProxy(object):

    def registry(self, server, app_name, instance_host, instance_port, status_page_url, health_check_url,
                 renewal_interval_in_secs, duration_in_secs):
        """
        注册服务
        :return:
        """
        pass

    def registry_discovery(self, server, renewal_interval_in_secs):
        """
        仅仅注册监听器
        :param server:
        :param renewal_interval_in_secs:
        :return:
        """
        pass

    def deregistry(self):
        """
        反注册服务
        :return:
        """
        pass

    def heartbeat(self):
        """
        心跳
        :return:
        """
        pass

    def check_instance_available(self, app_name):
        """
        判断某个服务是否有实例
        :param app_name:
        :return:
        """
        pass

    def do_service(self, service="", return_type="json", app_name="sobeyficus",
                   prefer_ip=False, prefer_https=False,
                   method="GET", headers=None, params=None,
                   data=None, timeout=None, auth=True):
        """
        调用其他服务
        :param service:
        :param return_type:
        :param app_name:
        :param prefer_ip:
        :param prefer_https:
        :param method:
        :param headers:
        :param params:
        :param data:
        :param timeout:
        :param auth:
        :return:
        """
        pass


@Value("${discovery.type:eureka}")
def discovery_type(self):
    pass


class DiscoveryServiceProxyFactory(Singleton):
    __instance = None

    def get_discovery_service_proxy(self, mode: str = None) -> DiscoveryServiceProxy:
        if self.__instance:
            return self.__instance

        if mode is None:
            mode = discovery_type()

        if mode == "eureka":
            self.__instance = EurekaDiscoveryServiceProxy.instance()
        else:
            self.__instance = ConsulDiscoveryServiceProxy.instance()

        return self.__instance


class EurekaDiscoveryServiceProxy(DiscoveryServiceProxy, Singleton):
    def registry(self, server, app_name, instance_host, instance_port, status_page_url, health_check_url,
                 renewal_interval_in_secs, duration_in_secs):
        eureka_client.init(eureka_server=server,
                           app_name=app_name,
                           # 当前组件的主机名，可选参数，如果不填写会自动计算一个，如果服务和 eureka 服务器部署在同一台机器，请必须填写，否则会计算出 127.0.0.1
                           instance_host=instance_host,
                           instance_port=instance_port,
                           # 调用其他服务时的高可用策略，可选，默认为随机
                           ha_strategy=eureka_client.HA_STRATEGY_STICK,
                           status_page_url=status_page_url,
                           health_check_url=health_check_url,
                           renewal_interval_in_secs=renewal_interval_in_secs,
                           duration_in_secs=duration_in_secs)

    def registry_discovery(self, server, renewal_interval_in_secs):
        eureka_client.init_discovery_client(eureka_server=server, renewal_interval_in_secs=renewal_interval_in_secs)

    def deregistry(self):
        # 这个不需要
        pass

    def check_instance_available(self, app_name):

        from config import work_on_k8s
        if not work_on_k8s:
            # 如果没有在k8s上,就去从注册中心上找
            cli = eureka_client.get_discovery_client()
            if cli is None:
                raise Exception("Discovery Client has not initialized. ")
            app = cli.applications.get_application(app_name.upper())
            if app.instances is None or len(app.instances) == 0:
                raise ServiceNoInstanceException(f"{app_name}服务没有找到可用的实例")
        # 如果在k8s上,就不需要去判断

    def heartbeat(self):
        # 这个不需要
        pass

    def do_service(self, service="", return_type="json", app_name="sobeyficus", prefer_ip=False, prefer_https=False,
                   method="GET", headers=None, params=None, data=None, timeout=None, auth=True):
        def walk_using_requests(url):
            from client.ClientAuth import ClientAuth
            global r
            try:
                if method.lower() == "get":
                    r = requests.get(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                     timeout=timeout, params=params)
                elif method.lower() == "post":
                    r = requests.post(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                      timeout=timeout, params=params)
                elif method.lower() == "put":
                    r = requests.put(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                     timeout=timeout, params=params)
                elif method.lower() == "patch":
                    r = requests.patch(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                       timeout=timeout, params=params)
                elif method.lower() == "delete":
                    r = requests.delete(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                        timeout=timeout, params=params)
                else:
                    raise IllegalArgumentException(f"不支持的Rest操作:{method}")
                r.raise_for_status()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                from urllib.error import HTTPError
                raise HTTPError(url, 500, "连接错误或超时", str(e), None)

            try:
                if return_type is None or return_type.lower() == "none":
                    return None

                if len(r.content) <= 0:
                    return None

                if return_type.lower() in ("json", "dict", "dictionary"):
                    r.encoding = 'utf-8'
                    return r.json()
                else:
                    r.encoding = 'utf-8'
                    return r.text
            finally:
                r.close()

        cli = eureka_client.get_discovery_client()
        if cli is None:
            raise Exception("Discovery Client has not initialized. ")

        return cli.walk_nodes(app_name, service, prefer_ip, prefer_https, walk_using_requests)


class ConsulDiscoveryServiceProxy(DiscoveryServiceProxy, Singleton):
    __cons: consul.Consul = None
    __service_id = None

    def registry(self, server: str, app_name, instance_host, instance_port, status_page_url, health_check_url,
                 renewal_interval_in_secs, duration_in_secs):
        splited = server.split(':')
        self.__cons = consul.Consul(host=splited[0], port=int(splited[1]))
        self.__service_id = f"{app_name}-{instance_port}"
        index = 1
        while True:
            if index > 10:
                _logger.error(f'consul host is down, already retry:{index} times,Exit')
                exit(-1)
            try:
                self.__cons.agent.service.register(name=app_name, address=instance_host,
                                                   port=instance_port, service_id=self.__service_id,
                                                   check=consul.Check.http(
                                                       f"http://{instance_host}:{instance_port}{health_check_url}",
                                                       f'{renewal_interval_in_secs}s',
                                                       '5s',
                                                       f'{duration_in_secs}s'))  # integrated service registration <3
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, consul.ConsulException):
                _logger.warn(f'consul host ({server}) is down, reconnecting... retry:{index}')
                index = index + 1
                sleep(0.5)

    def registry_discovery(self, server, renewal_interval_in_secs):
        """这个不需要实现"""
        pass

    def check_instance_available(self, app_name):
        node = self.__get_available_service(app_name)
        if node is None:
            raise ServiceNoInstanceException(f"{app_name}服务没有找到可用的实例")

    def deregistry(self):
        _logger.info(f"deregistry serivce: {self.__service_id}")
        if self.__cons is not None:
            self.__cons.agent.service.deregister(self.__service_id)

    def heartbeat(self):
        # 这个不需要
        pass

    def do_service(self, service="", return_type="json", app_name="sobeyficus", prefer_ip=True, prefer_https=False,
                   method="GET", headers=None, params=None, data=None, timeout=None, auth=True):

        def walk_using_requests(url):
            from client.ClientAuth import ClientAuth
            global r
            try:
                if method.lower() == "get":
                    r = requests.get(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                     timeout=timeout, params=params)
                elif method.lower() == "post":
                    r = requests.post(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                      timeout=timeout, params=params)
                elif method.lower() == "put":
                    r = requests.put(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                     timeout=timeout, params=params)
                elif method.lower() == "patch":
                    r = requests.patch(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                       timeout=timeout, params=params)
                elif method.lower() == "delete":
                    r = requests.delete(url, json=data, auth=ClientAuth() if auth else None, headers=headers,
                                        timeout=timeout, params=params)
                else:
                    raise IllegalArgumentException(f"不支持的Rest操作:{method}")
                r.raise_for_status()
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                from urllib.error import HTTPError
                raise HTTPError(url, 500, "连接错误或超时", str(e), None)

            try:
                if return_type is None or return_type.lower() == "none":
                    return None

                if len(r.content) <= 0:
                    return None

                if return_type.lower() in ("json", "dict", "dictionary"):
                    r.encoding = 'utf-8'
                    return r.json()
                else:
                    r.encoding = 'utf-8'
                    return r.text
            finally:
                r.close()

        # 找到一个可用的服务地址
        node = self.__get_available_service(app_name)
        error_nodes = []
        while node is not None:
            try:
                url = self.__generate_service_url(node, prefer_ip, prefer_https)
                if service.startswith("/"):
                    url = url + service[1:]
                else:
                    url = url + service
                return walk_using_requests(url)
            except (HTTPError, URLError):
                _logger.warn("do service %s in node [%s] error, use next node." % (service, node.ID))
                error_nodes.append(node.ID)
                node = self.__get_available_service(app_name, error_nodes)

        raise URLError("Try all up instances in registry, but all fail")

    # 思路就是去consul上去获取服务的实例列表
    def __get_available_service(self, application_name, ignore_instance_ids=None):
        # TODO 这里其实还应该增加一个简单的本地缓存的,否则请求consul太频繁
        index, instances = self.__cons.health.service(application_name, passing=True)
        up_instances = []

        if ignore_instance_ids is None or len(ignore_instance_ids) == 0:
            up_instances.extend(instances)
        else:
            for ins in instances:
                if ins["Service"]["ID"] not in ignore_instance_ids:
                    up_instances.append(ins)

        if len(up_instances) == 0:
            # no up instances
            return None
        elif len(up_instances) == 1:
            # only one available instance, then doesn't matter which strategy is.
            instance = Munch(up_instances[0]['Service'])
            # self.__ha_cache[application_name] = instance.instanceId
            return instance

        # 随机选一个
        def random_one(instances):
            if len(instances) == 1:
                idx = 0
            else:
                idx = random.randint(0, len(instances) - 1)
            selected_instance = Munch(instances[idx]['Service'])
            return selected_instance

        return random_one(up_instances)

    def __generate_service_url(self, instance, prefer_ip, prefer_https):
        if instance is None:
            return None
        schema = "http"
        port = 0
        if instance.Port and (len(instance.Tags) == 0 or "secure=false" in instance.Tags):
            schema = "http"
            port = instance.Port
        else:
            schema = "https"
            port = instance.Port

        host = instance.Address

        return "%s://%s:%d/" % (schema, host, port)


def discovery_service_proxy() -> DiscoveryServiceProxy:
    return DiscoveryServiceProxyFactory.instance().get_discovery_service_proxy()


@atexit.register
def deregistry():
    discovery_service_proxy().deregistry()
