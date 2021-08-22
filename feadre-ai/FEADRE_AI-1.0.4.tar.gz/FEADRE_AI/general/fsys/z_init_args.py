import socket
import sys

import cv2


def init_cfg():
    print('\n', sys.path)
    host_name = socket.gethostname()
    if host_name == 'Feadre-NB':
        path_host = 'M:'
        # raise Exception('当前主机: %s 及主数据路径: %s ' % (host_name, cfg.PATH_HOST))
    elif host_name == 'e2680v2':
        path_host = ''
    else:
        raise Exception('主机名不存在 %s ' % host_name)
    return path_host

