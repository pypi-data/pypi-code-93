import time
import uuid
from datetime import datetime


def dt_time():
    nnn = time.time() - 8 * 60 * 60
    dat = datetime.fromtimestamp(nnn)
    ttt = dat.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return ttt


def dt_now_time():
    nnn = time.time()
    dat = datetime.fromtimestamp(nnn)
    ttt = dat.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return ttt


def get_uuid():
    uid = str(uuid.uuid4())
    suid = "".join(uid.split("-"))
    return suid
