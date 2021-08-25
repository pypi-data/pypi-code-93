from __future__ import absolute_import
from __future__ import unicode_literals

import os
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from laipvt.helper.exception import UtilsError
from laipvt.sysutil.util import path_join, log

class Template(object):
    def __init__(self, data: dict, file_path: str, file_dest: str):
        self.file_path = file_path
        self.file_dest = file_dest
        self.data = data

    def template_handler(self, src: str) -> str:
        pass

    def _fill(self, src, dest):
        log.debug("渲染模板: {}到目录: {}".format(src, dest))
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        content = self.template_handler(src)
        with open(dest, 'w+', encoding='utf-8') as fp:
            fp.write(content)

    def fill(self):
        if os.path.isfile(self.file_path):
            file_path = self.file_path
            file_dest = self.file_dest
            self._fill(file_path, file_dest)
        elif os.path.isdir(self.file_path):
            if not os.path.exists(self.file_dest):
                os.makedirs(self.file_dest)
            self.fill_all(self.file_path, self.file_dest)
        else:
            log.error("self.file_path: {}, self.file_dest: ".format(self.file_path, self.file_dest))
            raise UtilsError("Template.fill, 错误信息: 目录类型不正确或目录不存在") from None

    def fill_all(self, src, dest):
        try:
            for root, dirs, files in os.walk(src):
                for file_name in files:
                    file_path = path_join(root, file_name)
                    if len(root) == len(src):
                        file_dest = path_join(dest, file_name)
                        log.info("渲染模板到{}".format(path_join(dest, file_name)))
                    else:
                        new_path = root.replace("{}/".format(src), "")
                        while True:
                            if new_path.startswith("/"):
                                new_path = new_path[1:]
                            else:
                                break
                        file_dest = path_join(dest, new_path, file_name)
                        log.debug("找到子目录下的文件")
                        log.info("渲染模板到{}".format(file_dest))
                    self._fill(file_path, file_dest)
        except Exception as e:
            raise UtilsError("FileTemplate.fill_all, 错误信息: {}".format(e)) from None

    def run(self):
        pass


class FileTemplate(Template):
    def __init__(self, data, file_path, file_dest):
        super().__init__(data, file_path, file_dest)

    def template_handler(self, src):
        try:
            loader = FileSystemLoader(src)
            env = Environment(loader=loader, undefined=StrictUndefined)
            return env.get_template('').render(self.data)

        except Exception as e:
            raise UtilsError("FileTemplate.template_handler, 错误信息: {}".format(e)) from None


class ConfigMapTemplate(Template):
    def __init__(self):
        super().__init__()
