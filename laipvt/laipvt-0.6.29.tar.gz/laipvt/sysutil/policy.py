from __future__ import absolute_import
from __future__ import unicode_literals

import socket
import re
import os

def is_port(port):
    try:
        return True if int(port) >= 0 and int(port) < 65536 else False
    except Exception:
        return False

def is_ip_or_fqdn(ip):
    try:
        res = socket.getaddrinfo(ip, 0, socket.AF_UNSPEC,
                                 socket.SOCK_STREAM,
                                 0, socket.AI_NUMERICHOST)
        return bool(res)
    except Exception:
        pattern = re.compile(
            r'^(([a-zA-Z]{1})|([a-zA-Z]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z]{1}[0-9]{1})|([0-9]{1}[a-zA-Z]{1})|'
            r'([a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
            r'([a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})$'
        )
        return True if pattern.match(ip) else False

def is_password(password: str) -> bool:
    try:
        return True if re.search("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).*$", password) and len(password) >= 8 else False
    except Exception:
        return False

def is_dir(path: str) -> bool:
    return os.path.isdir(path)

def is_file(path: str) -> bool:
    return os.path.isfile(path)