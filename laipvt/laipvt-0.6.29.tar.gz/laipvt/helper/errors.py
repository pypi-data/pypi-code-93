from __future__ import absolute_import
from __future__ import unicode_literals

import os
from laipvt.sysutil.gvalue import DEPLOY_LANGUAGE

class Error():
    def __init__(self):
        lang = os.environ.get("DEPLOY_LANGUAGE", DEPLOY_LANGUAGE)
        map = {
            "en": self.en,
            "cn": self.cn
        }
        try:
            map[lang]()
        except KeyError:
            self.cn()

    def cn(self):
        self.UNIMPLEMENT_ERROR = "未实现的方法: {}"
        self.USER_EXIT = "用户手动退出。程序结束"

    def en(self):
        self.UNIMPLEMENT_ERROR = "un implement function: {}"
        self.USER_EXIT = "user exit. quit process"

class PackageErrors(Error):
    def __init__(self):
        super(PackageErrors, self).__init__()

    def cn(self):
        self.PROJECT_ID_UNMATCH = "授权id与实际申请的项目不匹配"
        self.PROJECT_ID_INCORRECT = "授权id不正确"
        self.PACKAGE_ILLEGAL = "文件不合法，{}不存在"
        self.UNPACK_ERROR = "文件解压失败，错误信息: {}"
        self.PACK_ERROR = "文件打包失败，错误信息: {}"

    def en(self):
        self.PROJECT_ID_UNMATCH = "authorization id is unmatch with this project"
        self.PROJECT_ID_INCORRECT = "incorrect authorization id"
        self.PACKAGE_ILLEGAL = "file type illegal，{} is not exist"
        self.UNPACK_ERROR = "file unpack failed, error msg: {}"
        self.PACK_ERROR = "package file failed, error msg: {}"

class FileTypeErrors(Error):
    def __init__(self):
        super(FileTypeErrors, self).__init__()

    def cn(self):
        self.WRONG_FILE_TYPE = "不支持的文件类型"

    def en(self):
        self.WRONG_FILE_TYPE = "unsupported file type"

class RuntimeErrors(Error):
    def __init__(self):
        super(RuntimeErrors, self).__init__()

    def cn(self):
        self.SEND_FILE_ERROR = "发送文件{}, 到服务器: {} 失败。错误信息: {}"
        self.RUN_CMD_ERROR = "在服务器: {} 执行命令 {} 失败。错误信息: {}"

    def en(self):
        self.SEND_FILE_ERROR = "Failed send {} to server: {}. Error message: {}"
        self.RUN_CMD_ERROR = "Server: {}. Run command {} failed. Error message: {}"