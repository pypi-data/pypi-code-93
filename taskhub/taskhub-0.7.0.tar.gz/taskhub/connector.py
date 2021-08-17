from .hub import TaskHub, HubManager

def connect(ip:str,port:int,passwd:str):
    """[连接到taskhub server]

    Args:
        ip (str): [server 的ip地址]
        port (int): [server 的使用的端口]
        passwd (str): [连接密码]

    Returns:
        [TaskHub]: [返回连接器对象]
    """
    HubManager.register('get_hub')
    m = HubManager(address=(ip,port), authkey=passwd.encode("utf-8"))
    m.connect()
    return m.get_hub()
