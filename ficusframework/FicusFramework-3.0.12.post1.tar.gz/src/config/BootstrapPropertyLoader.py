import logging
import config

log = logging.getLogger('Ficus')


def load_properties_after_started(app):
    """
    加载配置文件  bootstrap.yml
    :param app:
    :return:
    """
    # 1. 获取yaml文件
    if _exists_bootstrap_property(app) is None:
        return

    # 这里开始尝试访问cloud-config获取配置文件
    from client import check_instance_avaliable
    from api.exceptions import ServiceNoInstanceException
    try:
        check_instance_avaliable(config.config_server_id)
    except ServiceNoInstanceException:
        if config.config_fail_fast:
            from api.exceptions import ServiceNoInstanceException
            raise ServiceNoInstanceException("cloud-config服务没有启动,系统启动失败")
        else:
            log.info("没有从注册中心上找到配置中心,使用默认配置")
        return

    # region 发起请求 获取配置,并设置到 annotation.REMOTE_YML_CONFIG 中
    from urllib.error import HTTPError
    try:
        # 支持配置多个
        configs = config.config_name.split(",")
        from client import do_service
        for conf in configs:
            r = do_service(f"{conf}-{config.config_profile}.yml", app_name=config.config_server_id,
                           return_type="str", auth=False)  # 这里是从配置中心去获取数据,不做auth
            # 配置中心的配置文件不存在时，返回的是 '{}'
            if r is not None and str(r).rstrip() != '{}':
                from config import annotation
                import yaml
                # 合并本地配置文件和云端配置文件
                annotation.deep_search_and_merge(annotation.REMOTE_YML_CONFIG,
                                                 yaml.load(r, Loader=yaml.FullLoader))  # r.content
                log.info(f"完成配置中心配置读取{conf}-{config.config_profile}")
            else:
                from api.exceptions import ServiceInnerException
                raise ServiceInnerException(f"cloud-config服务没有 {conf}-{config.config_profile}.yml 配置")
    except HTTPError:
        if config.config_fail_fast:
            from api.exceptions import ServiceNoInstanceException
            raise ServiceNoInstanceException("cloud-config服务没有启动,系统启动失败")
        else:
            # 如果不快速失败,就直接返回
            return
    # endregion


def _exists_bootstrap_property(app):
    from registry import read_yaml_file
    yml = read_yaml_file(app, "bootstrap.yml", config.spring_profiles_active)
    return yml


def init_from_yaml_property(app):
    """
    读取本地的配置文件
    :param app:
    :return:
    """

    # 先读取 applicaton.yml 文件
    _read_from_application_yaml_property(app)

    # 再读取bootstrap.yml 文件
    yml = _exists_bootstrap_property(app)

    if yml is None:
        # 说明没有yml文件,不进行注册处理
        log.info("没有配置bootstrap.yml,采用默认的配置信息")
        return False

    # 说明有yml文件,开始进行处理

    # 第一个: server.port
    if "server" in yml and "port" in yml["server"]:
        config.server_port = yml["server"]["port"]

    if "server" in yml and "ip" in yml["server"]:
        config.server_ip = yml["server"]["ip"]

    try:
        config.config_name = yml["spring"]["cloud"]["config"]["name"]
    except:
        pass

    try:
        config.config_profile = yml["spring"]["cloud"]["config"]["profile"]
    except:
        pass

    try:
        config.config_server_id = yml["spring"]["cloud"]["config"]["discovery"]["service-id"]
    except:
        pass

    try:
        config.config_fail_fast = yml["spring"]["cloud"]["config"]["fail-fast"]
    except:
        pass

    try:
        config.application_name = yml["spring"]["application"]["name"]
    except:
        pass

    try:
        config.eureka_default_zone = yml["eureka"]["client"]["service-url"]["defaultZone"]
    except:
        try:
            config.eureka_default_zone = f"{yml['spring']['cloud']['consul']['host']}:{yml['spring']['cloud']['consul']['port']}"
        except:
            pass

    try:
        config.eureka_default_zone = f"{yml['spring']['cloud']['consul']['host']}:{yml['spring']['cloud']['consul']['port']}"
    except:
        pass

    return True


def init_profile_from_environ_property():
    import os

    environs = os.environ

    if "spring.profiles.active" in environs:
        config.spring_profiles_active = environs["spring.profiles.active"]
        log.info(f"从系统环境变量中获取到spring.profiles.active:{config.spring_profiles_active}")
    elif "SPRING_PROFILES_ACTIVE" in environs:
        config.spring_profiles_active = environs["SPRING_PROFILES_ACTIVE"]
        log.info(f"从系统环境变量中获取到SPRING_PROFILES_ACTIVE:{config.spring_profiles_active}")

    if "WORK_ON_K8S" in environs:
        config.work_on_k8s = bool(environs["WORK_ON_K8S"])
        log.info(f"从系统环境变量中获取到WORK_ON_K8S:{config.work_on_k8s}")

    if "K8S_AUTH_SERVER_SERVICE" in environs:
        config.k8s_auth_server_service = environs["K8S_AUTH_SERVER_SERVICE"]
        log.info(f"从系统环境变量中获取到K8S_AUTH_SERVER_SERVICE:{config.k8s_auth_server_service}")

    if "K8S_CONFIG_SERVER_SERVICE" in environs:
        config.k8s_config_server_service = environs["K8S_CONFIG_SERVER_SERVICE"]
        log.info(f"从系统环境变量中获取到K8S_CONFIG_SERVER_SERVICE:{config.k8s_config_server_service}")

    if "K8S_FICUS_SERVER_SERVICE" in environs:
        config.k8s_ficus_server_service = environs["K8S_FICUS_SERVER_SERVICE"]
        log.info(f"从系统环境变量中获取到K8S_FICUS_SERVER_SERVICE:{config.k8s_ficus_server_service}")

    if "K8S_SCHEDULE_SERVER_SERVICE" in environs:
        config.k8s_schedule_server_service = environs["K8S_SCHEDULE_SERVER_SERVICE"]
        log.info(f"从系统环境变量中获取到K8S_SCHEDULE_SERVER_SERVICE:{config.k8s_schedule_server_service}")


def init_from_environ_property():
    import os

    environs = os.environ
    # 第一个: server.port
    if "server.port" in environs:
        config.server_port = int(environs["server.port"])
        log.info(f"从系统环境变量中获取到server.port:{config.server_port}")
    elif "SERVER_PORT" in environs:
        config.server_port = int(environs["SERVER_PORT"])
        log.info(f"从系统环境变量中获取到SERVER_PORT:{config.server_port}")

    if "server.ip" in environs:
        config.server_ip = environs["server.ip"]
        log.info(f"从系统环境变量中获取到server.ip:{config.server_ip}")
    elif "SERVER_IP" in environs:
        config.server_ip = environs["SERVER_IP"]
        log.info(f"从系统环境变量中获取到SERVER_IP:{config.server_ip}")

    if "spring.cloud.config.name" in environs:
        config.config_name = environs["spring.cloud.config.name"]
        log.info(f"从系统环境变量中获取到spring.cloud.config.name:{config.config_name}")
    elif "SPRING_CLOUD_CONFIG_NAME" in environs:
        config.config_name = environs["SPRING_CLOUD_CONFIG_NAME"]
        log.info(f"从系统环境变量中获取到SPRING_CLOUD_CONFIG_NAME:{config.config_name}")

    if "spring.cloud.config.profile" in environs:
        config.config_profile = environs["spring.cloud.config.profile"]
        log.info(f"从系统环境变量中获取到spring.cloud.config.profile:{config.config_profile}")
    elif "SPRING_CLOUD_CONFIG_PROFILE" in environs:
        config.config_profile = environs["SPRING_CLOUD_CONFIG_PROFILE"]
        log.info(f"从系统环境变量中获取到SPRING_CLOUD_CONFIG_PROFILE:{config.config_profile}")

    if "spring.cloud.config.fail-fast" in environs:
        config.config_fail_fast = bool(environs["spring.cloud.config.fail-fast"])
        log.info(f"从系统环境变量中获取到spring.cloud.config.fail-fast:{config.config_fail_fast}")
    elif "SPRING_CLOUD_CONFIG_FAILFAST" in environs:
        config.config_fail_fast = bool(environs["SPRING_CLOUD_CONFIG_FAILFAST"])
        log.info(f"从系统环境变量中获取到SPRING_CLOUD_CONFIG_FAILFAST:{config.config_fail_fast}")

    if "spring.cloud.config.discovery.service-id" in environs:
        config.config_server_id = environs["spring.cloud.config.discovery.service-id"]
        log.info(f"从系统环境变量中获取到spring.cloud.config.discovery.service-id:{config.config_server_id}")
    elif "SPRING_CLOUD_CONFIG_DISCOVERY_SERVICEID" in environs:
        config.config_server_id = environs["SPRING_CLOUD_CONFIG_DISCOVERY_SERVICEID"]
        log.info(f"从系统环境变量中获取到SPRING_CLOUD_CONFIG_DISCOVERY_SERVICEID:{config.config_server_id}")

    if "spring.application.name" in environs:
        config.application_name = environs["spring.application.name"]
        log.info(f"从系统环境变量中获取到spring.application.name:{config.application_name}")
    elif "SPRING_APPLICATION_NAME" in environs:
        config.application_name = environs["SPRING_APPLICATION_NAME"]
        log.info(f"从系统环境变量中获取到SPRING_APPLICATION_NAME:{config.application_name}")

    if "eureka.client.service-url.defaultZone" in environs:
        config.eureka_default_zone = environs["eureka.client.service-url.defaultZone"]
        log.info(f"从系统环境变量中获取到eureka.client.service-url.defaultZone:{config.eureka_default_zone}")
    elif "EUREKA_CLIENT_SERVICEURL_DEFAULTZONE" in environs:
        config.eureka_default_zone = environs["EUREKA_CLIENT_SERVICEURL_DEFAULTZONE"]
        log.info(f"从系统环境变量中获取到EUREKA_CLIENT_SERVICEURL_DEFAULTZONE:{config.eureka_default_zone}")

    if "spring.cloud.consul.host" in environs and "spring.cloud.consul.port" in environs:
        config.eureka_default_zone = f"{environs['spring.cloud.consul.host']}:{environs['spring.cloud.consul.port']}"
        log.info(f"从系统环境变量中获取到spring.cloud.consul.host:{config.eureka_default_zone}")
    elif "SPRING_CLOUD_CONSUL_HOST" in environs and "SPRING_CLOUD_CONSUL_PORT" in environs:
        config.eureka_default_zone = f"{environs['SPRING_CLOUD_CONSUL_HOST']}:{environs['SPRING_CLOUD_CONSUL_PORT']}"
        log.info(f"从系统环境变量中获取到spring.cloud.consul.host:{config.eureka_default_zone}")

def _read_from_application_yaml_property(app):
    """
    读取本地的文件到系统配置中
    :param app:
    :return:
    """
    from registry import read_yaml_file
    yml = read_yaml_file(app, "application.yml", config.spring_profiles_active)
    if yml is None:
        # 说明没有yml文件,不进行注册处理
        log.info("没有配置application.yml,采用默认的配置信息")
        return
    from config import annotation
    # 把本地的信息加入到配置中
    annotation.REMOTE_YML_CONFIG = yml

    try:
        config.actor_name = yml["actor"]["name"]
    except:
        pass
