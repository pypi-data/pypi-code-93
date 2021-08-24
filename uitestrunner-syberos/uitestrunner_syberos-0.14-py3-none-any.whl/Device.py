import base64
import os

from . import Connection
from . import Application
from . import Events
from urllib3 import encode_multipart_formdata
import configparser


class Device(Events.Events):
    con = Connection.Connection()
    __osVersion = ""
    __serialNumber = ""
    xmlStr = ""
    __xpath_file = "../../xpath_list.ini"
    __screenshots = "./screenshots/"
    default_timeout = 30

    def __init__(self, host="192.168.100.100", port=8080):
        super().__init__(d=self)
        self.con.host = host
        self.con.port = port
        self.con.connect()
        self.__serialNumber = str(self.con.get(path="getSerialNumber").read(), 'utf-8')
        self.__osVersion = str(self.con.get(path="getOsVersion").read(), 'utf-8')

    def set_default_timeout(self, timeout):
        self.default_timeout = timeout

    def set_xpath_list(self, path):
        self.__xpath_file = path

    def set_screenshots_path(self, path):
        self.__screenshots = path

    def screenshot(self, path=__screenshots):
        if not os.path.exists(path):
            os.makedirs(path)
        img_base64 = str(self.con.get(path="getScreenShot").read(), 'utf-8')
        current_remote_time = self.con.get(path="getSystemTime").read()
        image = open(path + "/" + str(current_remote_time, 'utf-8') + ".png", "wb")
        image.write(base64.b64decode(img_base64))
        image.close()

    def get_xpath(self, sopid, key):
        if not os.path.exists(self.__xpath_file):
            f = open(self.__xpath_file, "w")
            f.close()
        conf = configparser.ConfigParser()
        conf.read(self.__xpath_file)
        return conf.get(sopid, key)

    def application(self, sopid, uiappid):
        return Application.Application(d=self, sop=sopid, ui=uiappid)

    def refresh_layout(self):
        self.xmlStr = str(self.con.get(path="getLayoutXML").read(), 'utf-8')

    def os_version(self):
        return self.__osVersion

    def serial_number(self):
        return self.__serialNumber

    def upload_file(self, file_path, remote_path):
        file_name = file_path.split("/")[len(file_path.split("/")) - 1]
        if file_name == "":
            raise Exception('error: the file path format is incorrect, and the transfer folder is not supported')
        if remote_path.split("/")[len(remote_path.split("/")) - 1] == "":
            remote_path += file_name
        header = {
            "content-type": "application/json",
            "FileName": remote_path
        }
        data = {'file': (file_name, open(file_path, 'rb').read())}
        encode_data = encode_multipart_formdata(data)
        data = encode_data[0]
        header['Content-Type'] = encode_data[1]
        return bool(int(str(self.con.post(path="upLoadFile", headers=header, data=data).read(), 'utf-8')))

    def file_exist(self, file_path):
        return bool(int(str(self.con.get(path="checkFileExist", args="filename=" + file_path).read(), 'utf-8')))

    def dir_exist(self, dir_path):
        return self.file_exist(dir_path)

    def mkdir(self, dir_path):
        return bool(int(str(self.con.get(path="mkdir", args="dirname=" + dir_path).read(), 'utf-8')))

    def is_installed(self, sopid):
        return bool(int(str(self.con.get(path="isAppInstalled", args="sopid=" + sopid).read(), 'utf-8')))

    def is_uninstallable(self, sopid):
        return bool(int(str(self.con.get(path="isAppUninstallable", args="sopid=" + sopid).read(), 'utf-8')))

    def install(self, file_path):
        if self.upload_file(file_path, "/tmp/"):
            file_name = file_path.split("/")[len(file_path.split("/")) - 1]
            self.con.get(path="install", args="filepath=/tmp/" + file_name)
            return True
        return False

    def uninstall(self, sopid):
        return bool(int(str(self.con.get(path="uninstall", args="sopid=" + sopid).read(), 'utf-8')))

