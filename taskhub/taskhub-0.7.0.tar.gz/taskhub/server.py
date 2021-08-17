
from .hub import TaskHub, HubManager
from .connector import connect
from multiprocessing import Process
import time


def start_hub_serve(ip, port, passwd, sync):
    hub = TaskHub(sync)
    HubManager.register('get_hub', callable=lambda: hub)
    hubmanager = HubManager(address=(ip, port), authkey=passwd.encode("utf-8"))
    serve = hubmanager.get_server()
    serve.serve_forever()


def serve(ip: str, port: int, passwd: str, sync):
    """[启动taskhub服务]

    Args:
        port (int): [端口]
        passwd (str): [设置密码，连接到本taskhub需要提供]
        sync ([type]): [同步函数，接受一个“done”状态的Task，
        该函数负责处理这些完成状态的数据，并返回一个bool值，
        以表示处理成功与否，若成功taskhub将移除改该Task]
    """

    p = Process(target=start_hub_serve, args=(ip, port, passwd, sync,))
    p.start()
    time.sleep(3)
    hub = connect(ip, port, passwd)
    hub.serve()
