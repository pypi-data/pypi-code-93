from __future__ import absolute_import
from __future__ import unicode_literals

import os
import json
import re
import time
import string
import shutil
import array
import base64
import requests
import netifaces
import subprocess

from IPy import IP
from random import choice
from laipvt.sysutil.conf import YamlConfig, JsonConfig
from laipvt.sysutil.log import Logger
from laipvt.helper.exception import UtilsError
from laipvt.sysutil.ssh import SSHConnect, monkey_sudo, to_str
from laipvt.sysutil.status import Status
from laipvt.sysutil.gvalue import LAIPVT_LOG_PATH, LAIPVT_LOG_NAME, LAIPVT_LOG_LEVEL, LOG_TO_TTY
from laipvt.sysutil.command import gen_server_key_cmd, gen_ca_crt_cmd, gen_server_crt_cmd, gen_server_csr_cmd, \
    gen_server_secure_key_cmd


log = Logger(
    log_path=os.environ.get("LOG_PATH", LAIPVT_LOG_PATH),
    log_name=os.environ.get("LOG_NAME", LAIPVT_LOG_NAME),
    log_level=os.environ.get("LOG_LEVEL", LAIPVT_LOG_LEVEL),
    tty=os.environ.get("LOG_TO_TTY", LOG_TO_TTY)
).get()

def ssh_obj(ip, user, password, port=22) -> SSHConnect:
    return SSHConnect(hostip=ip, username=user, password=password, port=port)

def path_join(path_1: str, *args: str):
    return os.path.join(path_1, *args)

def gen_pass(len=12):
    char = string.digits + string.ascii_letters
    r = re.compile("\d")
    while True:
        passwd = "".join([choice(char) for i in range(len)])
        if r.match(passwd):
            return passwd

def to_object(d: [dict, list]):
    if isinstance(d, list):
        d = [to_object(x) for x in d]
    if not isinstance(d, dict):
        return d
    class C(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__
        # def get(self, key):
        #     d = self.__dict__
        #     return d[key]
        # def to_dict(self):
        #     return self.__dict__
    o = C()
    for k in d:
        o[k] = to_object(d[k])
    return o

def get_yaml_config(path):
    cfg = YamlConfig(path)
    return cfg.read_file()

def get_json_config(path):
    cfg = JsonConfig(path)
    return cfg.read_file()

def get_yaml_obj(path):
    return to_object(get_yaml_config(path))

def get_json_obj(path):
    return to_object(get_json_config(path))

def to_json(data):
    j = JsonConfig("", data=data)
    return j.read_from_data()

def file_run_able(path):
    if os.path.isfile(path):
        if os.access(path, os.X_OK):
            return True
        else:
            return False
    else:
        raise UtilsError("%s 不是合法的文件或文件不存在" % path)

def run_local_cmd(cmd, password=""):
    if password:
        cmd = monkey_sudo(password, cmd)
    code, stdout = subprocess.getstatusoutput(cmd)
    response = {
        "code": code,
        "stdout": to_str(stdout)
    }
    return to_object(response)

def local_copy(src, dest, password=""):
    cmd = "unalias -a; cp -af {} {}".format(src, dest)
    return run_local_cmd(cmd, password)

def upload(uploader, dest, src, local_path=""):
    if local_path:
        local_copy(src, local_path)
    else:
        uploader.upload_file(dest, src)

def download(path: str, url: str, file=""):
    r = requests.get(url, verify=False)
    f = os.path.join(path, file)
    if not file:
        f = os.path.join(path, url.split("/")[-1])
    with open(f, "wb") as fp:
        fp.write(r.content)
    return f

def pack(path, name, zip=False, dir_name=""):
    if not dir_name:
        dir_name = name
    cmd = "cd {} && tar cf {}.tar {}"
    p = os.path.join(path, "{}.tar".format(name))
    if zip:
        cmd = "cd {} && tar zcf {}.tar.gz {}"
        p = os.path.join(path, "{}.tar.gz".format(name))
    res = run_local_cmd(cmd.format(path, name, dir_name))
    if res.code == 0:
        return os.path.join(path, p)
    return False

def unpack(path, name, zip=False):
    cmd = "tar xmf {} -C {}"
    if zip:
        cmd = "tar zmxf {} -C {}"
    res = run_local_cmd(cmd.format(name, path))
    if res.code == 0:
        return True
    return False

def remove(path):
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)
    else:
        return False
    return True

def find(path, reg, file=False):
    r = re.compile(reg)
    for root, dirs, files in os.walk(path):
        real_path = os.path.abspath(root)
        if file:
            target = files
        else:
            target = dirs
        for n in target:
            if r.match(n):
                return path_join(real_path, n)
    return False

def encode(set_array, max_len=128):
    # 向上取整
    arr_l = int((max_len + 8 - 1) / 8)
    # B代表1个字节，8bit
    arr = array.array("B", [0 for _ in range(arr_l)])
    for v in set_array:
        v = int(v)
        if v > (max_len - 1):
            raise Exception("overflow")
        arr_idx = int(v / 8)
        byte_idx = v % 8
        arr[arr_idx] = arr[arr_idx] | 1 << byte_idx
    bs = base64.encodebytes(arr.tobytes()).decode("utf8")
    # 移除掉最后的=
    return bs[0:-1]

def decode(string, max_len=128):
    # 补齐=号
    string = string + "="
    byte = base64.decodebytes(string.encode("utf8"))
    arr = array.array("B", byte)
    result = []
    for idx in range(max_len):
        arr_idx = int(idx / 8)
        byte_idx = idx % 8
        if arr[arr_idx] & (1 << byte_idx):
            result.append(idx)
    result.sort()
    return result

def get_local_net_info():
    nic = netifaces.gateways()['default'][netifaces.AF_INET][1]
    gw = netifaces.gateways()['default'][netifaces.AF_INET][0]
    for interface in netifaces.interfaces():
        if interface == nic:
            mac = netifaces.ifaddresses(interface)[netifaces.AF_LINK][0]['addr']
            try:
                ip = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['addr']
                netmask = netifaces.ifaddresses(interface)[netifaces.AF_INET][0]['netmask']
            except KeyError:
                pass
    return {
        "name": nic,
        "gw": gw,
        "mac": mac,
        "ip": ip,
        "netmask": netmask
    }

def get_net_segment(ip='', netmask=''):
    _ip = ip
    _netmask = netmask
    if not ip and not netmask:
        res = get_local_net_info()
        _ip = res['ip']
        _netmask = res['netmask']
    return IP(_ip).make_net(_netmask).strNormal()

def post(url, data=None, json=None, **kwargs):
    try:
        res = requests.post(url, data=data, json=json, **kwargs)
        return res
    except Exception as e:
        log.error(e)
        exit(1)

def put(url, data=None, **kwargs):
    try:
        res = requests.put(url, data=data, **kwargs)
        return res
    except Exception as e:
        log.error(e)
        exit(1)


def get(url, params=None, **kwargs):
    try:
        res = requests.get(url, params=None, **kwargs)
        return res
    except Exception as e:
        log.error(e)
        exit(1)

def walk_sql_path(path):
    db_info = {}
    if os.path.exists(path):
        allfilelist = os.listdir(path)
        for dir_name in allfilelist:
            filepath = os.path.join(path, dir_name)
            if os.path.isdir(filepath):
                if not dir_name.startswith("."):
                    sql_list = []
                    for i in os.listdir(filepath):
                        if i.endswith(".sql"):
                            sql_list.append(os.path.join(filepath, i))
                    db_info[dir_name] = sql_list
    # print(db_info)
    return db_info


def status_me(proj):
    def run_func(fn):
        def wrapper(self, *args, **kwargs):
            status = Status()

            if status.get_status(proj, fn.__name__) == status.STATUS_SUCCESS:
                log.info("{}下的{}已经执行过，跳过当前步骤".format(proj, fn.__name__))
                return
            else:
                status.update_status(proj, fn.__name__, status.STATUS_FAILED)
                log.info("即将执行{}下的{}方法".format(proj, fn.__name__))
                fn(self, *args, **kwargs)
                status.update_status(proj, fn.__name__, status.STATUS_SUCCESS)
        return wrapper
    return run_func

def write_to_file(file_name, content=""):
    if not os.path.isdir(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(content)

def read_form_json_file(file_name):
    """
    读取json文件，返回dict
    """
    with open(file_name, "r") as fp:
         return json.load(fp)

def get_value_form_file(file_path, key):
    c = get_yaml_config(file_path)
    return c.get(key, False)

def backup_file(path):
    dir = os.path.dirname(path)
    if os.path.isdir(dir):
        backup_file_suffix = ".bak-%d" % int(time.time() * 1000)
        file_name = os.path.split(path)[1]
        backup_file = os.path.join(dir, file_name + backup_file_suffix)
        shutil.copyfile(path, backup_file)

def gen_https_self_signed_ca():
    https_ca_tmp_dir = "/tmp/certs"
    SERVER_SECURE_KEY = os.path.join(https_ca_tmp_dir, "server_secure.key")
    SERVER_KEY = os.path.join(https_ca_tmp_dir, "server.key")
    SERVER_CSR = os.path.join(https_ca_tmp_dir, "server.csr")
    CA_CRT = os.path.join(https_ca_tmp_dir, "ca.crt")
    SERVER_CRT = os.path.join(https_ca_tmp_dir, "server.crt")

    if not os.path.exists(https_ca_tmp_dir):
        os.mkdir(https_ca_tmp_dir)

    try:
        run_local_cmd(gen_server_secure_key_cmd.format(SERVER_SECURE_KEY))
        run_local_cmd(gen_server_key_cmd.format(SERVER_SECURE_KEY, SERVER_KEY))
        run_local_cmd(gen_server_csr_cmd.format(SERVER_KEY, SERVER_CSR))
        run_local_cmd(gen_ca_crt_cmd.format(SERVER_KEY, CA_CRT))
        run_local_cmd(gen_server_crt_cmd.format(SERVER_CSR, CA_CRT, SERVER_KEY, SERVER_CRT))
    except Exception as e:
        log.error("生成证书错误: {}".format(e))
        exit(1)
