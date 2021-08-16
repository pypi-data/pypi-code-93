#!/usr/bin/env python
from client.ClientAuth import ClientAuth
from discovery import discovery_service_proxy

FICUS_APP_NAME = "sobeyficus"


def do_service(service="", return_type="json", app_name=FICUS_APP_NAME,
               prefer_ip=False, prefer_https=False,
               method="GET", headers=None, params=None,
               data=None, timeout=None, auth=True, deep=0):
    try:
        return discovery_service_proxy().do_service(service, return_type, app_name, prefer_ip, prefer_https, method,
                                                headers, params, data, timeout, auth)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code >= 400 and e.response.status_code < 500 and e.response.status_code != 404:
            # 说明是认证的问题
            if auth:
                if deep >= 2:
                    raise e
                else:
                    # 那么这里就重新发一次
                    from client.ClientAuth import cancel_oauth_token
                    cancel_oauth_token()
                    return do_service(service, return_type, app_name, prefer_ip, prefer_https, method, headers, params, data, timeout, auth, deep+1)
            else:
                # 说明是不认证的
                raise e
        else:
            # 其他错误
            raise e


def check_instance_avaliable(app_name=FICUS_APP_NAME):
    discovery_service_proxy().check_instance_available(app_name)


from .ComputeExecutionClient import *
from .DataAlgorithmClient import *
from .DataCrawlClient import *
from .FactDatasourceClient import *
from .HandlerLogClient import *
from .JobScheduleClient import *
from .ScheduleCacheClient import *
from .ScheduleJobTaskLogClient import *
from .FactDatasourceManageClient import *
