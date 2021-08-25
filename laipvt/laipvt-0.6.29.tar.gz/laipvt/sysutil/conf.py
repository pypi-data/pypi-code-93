from __future__ import absolute_import
from __future__ import unicode_literals

import os
import re
import json
import time
from shutil import copyfile
from ruamel import yaml
from laipvt.sysutil.gvalue import STATUS_FILE, LAIPVT_BASE_DIR
from laipvt.helper.exception import UtilsError

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
status_file = STATUS_FILE


class ConfigInterface(object):
    """
        读取、写入文件通用接口
        读取文件调用read_file, 读取目录下文件调用read_dir
    """
    def __init__(self, path: str, data="", suffix=""):
        """
        :param path: 文件路径，可以是文件或者目录
        :param data: 要写入的数据，默认为空
        :param suffix: 如果path是目录，输入要匹配的文件结尾
        """
        self.data = data
        self.file_path = path
        self.multiple_file_path = []
        self.suffix = suffix
        self.file_suffix_regex = '.*\.%s$' % self.suffix

    def data_loader(self) -> str:
        pass

    def loader(self, p) -> dict:
        pass

    def writer(self):
        pass

    def multiple_loader(self):
        data_dict = {}
        for f in os.listdir(self.file_path):
            if re.match(self.file_suffix_regex, f):
                self.multiple_file_path.append(f)
        for real_file in self.multiple_file_path:
            try:
                data_dict.update(self.loader(os.path.join(self.file_path, real_file)))
            except Exception as e:
                raise UtilsError("读取文件{}失败".format(os.path.join(self.file_path, real_file)))
        return data_dict

    def read_from_data(self) -> str:
        return self.data_loader()

    def read_file(self) -> dict:
        try:
            if os.path.isfile(self.file_path):
                return self.loader(self.file_path)
            raise UtilsError("%s 文件不存在" % self.file_path)
        except json.decoder.JSONDecodeError:
            raise UtilsError("ConfigInterface.read_file 不是一个合法的json文件") from None

    def read_dir(self) -> dict:
        try:
            if os.path.isdir(self.file_path):
                return self.multiple_loader()
        except Exception as e:
            raise UtilsError("ConfigInterface.read_dir {}".format(e)) from None

    def backup_file(self, path):
        try:
            if os.path.isdir(path):
                backup_file_suffix = ".bak-%d" % int(time.time() * 1000)
                file_name = os.path.split(self.file_path)[1]
                backup_file = os.path.join(path, file_name + backup_file_suffix)
                copyfile(self.file_path, backup_file)
            else:
                raise UtilsError("%s 不是一个目录" % path)
        except Exception:
            raise UtilsError("ConfigInterface.backup_file") from None

    def write_file(self, backup=True, backup_path="/tmp"):
        if backup:
            self.backup_file(backup_path)
        self.writer()


class YamlConfig(ConfigInterface):

    def __init__(self, path, data="", suffix="yaml"):
        super().__init__(path, data, suffix=suffix)

    def data_loader(self) -> str:
        return yaml.dump(self.data)

    def loader(self, p):
        with open(p, "r", encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)

    def writer(self):
        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))
        with open(self.file_path, "w+", encoding="utf-8") as f:
            yaml.dump(self.data, f,
                      Dumper=yaml.RoundTripDumper, default_flow_style=False, allow_unicode=True, indent=4)

class JsonConfig(ConfigInterface):

    def __init__(self, path, data="", suffix="json"):
        super().__init__(path, data, suffix=suffix)

    def data_loader(self) -> str:
        return json.dumps(self.data)

    def loader(self, p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def writer(self):
        if not os.path.exists(os.path.dirname(self.file_path)):
            os.makedirs(os.path.dirname(self.file_path))
        with open(self.file_path, "w+", encoding="utf-8") as f:
            json.dump(self.data, f,
                      ensure_ascii=False, separators=(',', ':'), indent=4)

class AccountIdConfig(object):

    @classmethod
    def save(cls, account_id):
        with open(os.path.join(LAIPVT_BASE_DIR, "accountid.txt"), "w+", encoding="utf-8") as f:
            f.write(account_id)

    @classmethod
    def get(cls):
        with open(os.path.join(LAIPVT_BASE_DIR, "accountid.txt"), "r", encoding="utf-8") as f:
            content = f.read()
            return content.strip()
