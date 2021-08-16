server_ip = None
server_port = 5000
config_name = "sobey-cube"
config_profile = "release"
config_server_id = "sobeyficus-config-server"
config_fail_fast = True
eureka_default_zone = "http://sobeyficus:JXTYp9icQaTzs4@sobeyficus-eureka:8765/eureka/"
application_name = None
actor_name = None
spring_profiles_active = "default"

# 是否工作在K8S上, 如果在K8S上,那么在调用外部服务的时候,可以不通过注册中心,直接走K8S的服务发现
work_on_k8s = False
k8s_auth_server_service = "http://sc-auth-service.sobeyficus:80"        # 认证中心的完整地址
k8s_config_server_service = "http://config-server.sobeyficus:8777"        # 配置中心服务的完整地址
k8s_ficus_server_service = "http://sobeyficus.sobeyficus:8040"          # ficus核心服务的完整地址
k8s_schedule_server_service = "http://schedule-server.sobeyficus:8061"      # 调度服务的完整地址

def find_host_ip():
    """
    获取本机的IP地址
    :return:
    """
    import socket
    import config
    from urllib.parse import urlparse

    if config.server_ip is not None:
        return config.server_ip

    global s
    try:
        # 创建一个临时的socket连接
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 向自己发送一个udp的请求
        s.connect(('8.8.8.8', 80))
        # 送结果中获取到真实的ip地址
        config.server_ip = s.getsockname()[0]
    except Exception:
        pass
    finally:
        s.close()

    # 有时候通过8.8.8.8不连外网获取不到IP，所以这里再通过向eureka发送一个udp包来获取
    if config.server_ip is None and config.eureka_default_zone is not None:
        urls = config.eureka_default_zone.split(',')
        for url in urls:
            try:
                result = urlparse(url)
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # 发送一个udp的请求
                s.connect((result.hostname, result.port or 80))
                config.server_ip = s.getsockname()[0]
                return config.server_ip
            except Exception:
                pass
            finally:
                s.close()

    if config.server_ip is None:
        raise RuntimeError('获取本机IP失败')
    return config.server_ip
