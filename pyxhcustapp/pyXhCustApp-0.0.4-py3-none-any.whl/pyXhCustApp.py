import os
import sys
from os.path import isfile, join
from pathlib import Path
from typing import Optional


def is_win():
    return sys.platform == 'win32'


def is_linux():
    return sys.platform == 'linux'


def separator():
    if is_win():
        return '\\'
    elif is_linux():
        return '/'
    else:
        raise Exception("Unknown separator")


def _has_file(home, name: str) -> bool:
    return len([fileName for fileName in os.listdir(home) if fileName == name and isfile(join(home, fileName))]) == 1


def _get_file_content(home: str, name: str) -> Optional[str]:
    if _has_file(home, name):
        with open(join(home, name), 'r') as file:
            return file.read()
    else:
        return None


def _rm_file(home: str, name: str):
    os.remove(join(home, name))


def _kv_file_name(key: str) -> str:
    return "%s.kv" % (key)


def _set_kv(home: str, key: str, value: str):
    with open(join(home, _kv_file_name(key)), 'w') as file:
        file.write(value)


def _get_kv(home: str, key: str) -> Optional[str]:
    if _has_file(home, _kv_file_name(key)):
        with open(join(home, _kv_file_name(key))) as file:
            return file.read()
    else:
        return None


def _rm_kv(home: str, key: str):
    if _has_file(home, _kv_file_name(key)):
        _rm_file(home, _kv_file_name(key))


_PROXY_VAL = "proxy"


class CustApp:
    def __init__(self, home: Path, name: str):
        self.separator = separator()
        self.home = "%s%s.custApp%s%s" % (str(home), self.separator, self.separator, name)
        if os.path.exists(self.home) and os.path.isfile(self.home):
            raise Exception("Home %s is not directory!" % self.home)
        elif not os.path.exists(self.home):
            os.makedirs(self.home)

        if not os.path.exists(self.home) or os.path.isfile(self.home):
            raise Exception("Home %s is not valid!" % self.home)

    def has_proxy(self) -> bool:
        return _has_file(self.home, _PROXY_VAL)

    def proxy_value(self):
        return _get_file_content(self.home, _PROXY_VAL)

    def proxy_valid(self) -> bool:
        if self.has_proxy():
            value = self.proxy_value()
            os.path.exists(value) and os.path.isdir(value)
            return True
        else:
            return True

    def set_kv(self, key: str, value: str):
        _set_kv(self.home, key, value)

    def get_kv(self, key: str) -> Optional[str]:
        return _get_kv(self.home, key)

    def rm_kv(self, key: str) -> Optional[str]:
        if self.has_kv(key):
            v = self.get_kv(key)
            _rm_file(self.home, _kv_file_name(key))
            return v
        else:
            return None

    def has_kv(self, key: str) -> Optional[bool]:
        return _has_file(self.home, _kv_file_name(key))

    def list(self):
        files = list(map(lambda file_name: file_name[0:-3], os.listdir(self.home)))
        var_num = len(files)
        print("Number of variable: %s" % var_num)
        for file in files:
            print("%s: %s" % (file, self.get_kv(file)))

    @staticmethod
    def appDefault(name: str):
        return CustApp(Path.home(), name)


if __name__ == '__main__':
    def show_usage():
        script_str = "python -m pyXhCustApp {name_space}"
        print("%s list #Show all all" % script_str)
        print("%s exist {key} #return true if {key} exists " % script_str)
        print("%s value {key} #return value of {key} or None " % script_str)
        print("%s set {key} {value} #set {value} to {key} " % script_str)
        print("%s remove {key} #remove {key} " % script_str)


    if len(sys.argv) == 1:
        show_usage()
        exit(1)

    name_space = sys.argv[1]
    app = CustApp.appDefault(name_space)

    if len(sys.argv) == 2:
        show_usage()
        exit(1)

    cmd = sys.argv[2]
    if len(sys.argv) == 3:
        if cmd == "list":
            app.list()
            exit(0)

    if len(sys.argv) == 3:
        show_usage()
        exit(1)

    key = sys.argv[3]
    if len(sys.argv) == 4:
        if cmd == "exist":
            print("Contains key[%s]: %r" % (key, app.has_kv(key)))
            exit(0)
        if cmd == "value":
            print("%s: %s" % (key, app.get_kv(key)))
            exit(0)
        if cmd == "remove":
            if app.has_kv(key):
                print("Removed %s: %s" % (key, app.rm_kv(key)))
            else:
                print("key[%s] not exists" % key)
            exit(0)
        show_usage()
        exit(1)

    if len(sys.argv) == 5 and cmd == "set":
        value = sys.argv[4]
        app.set_kv(key, value)
        print("set key[%s] as %s" % (key, value))
        exit(0)

    show_usage()
    exit(1)
