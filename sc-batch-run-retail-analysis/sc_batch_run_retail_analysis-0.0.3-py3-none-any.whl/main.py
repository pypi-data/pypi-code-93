# The MIT License (MIT)
#
# Copyright (c) 2021 Scott Lau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import logging
import os
import os.path
from datetime import datetime

from sc_utilities import log_init

log_init()

from sc_retail_analysis.main import main as retail_main
from sc_diff_analysis.main import main as diff_main


class Runner:

    def __init__(self):
        pass

    def process_directory(self, dirname):
        conf_file = os.path.join(dirname, "production.yml")
        if not (os.path.exists(conf_file) and os.path.isfile(conf_file)):
            logging.getLogger(__name__).info("未找到配置文件，忽略此文件夹")
            return 0
        logging.getLogger(__name__).info("处理文件夹：%s", dirname)
        os.chdir(dirname)
        # 跑零售的时点分析
        return retail_main()

    def run(self):
        path = os.getcwd()
        date_dirs = list()
        # 扫描日期文件夹
        with os.scandir(path) as it:
            for entry in it:
                if entry.name.startswith('.') or entry.is_file():
                    continue
                try:
                    datetime.strptime(entry.name, "%Y%m%d")
                except ValueError:
                    # 不是日期文件夹，则忽略
                    continue
                date_dirs.append(entry.path)
        # 将文件夹按日期前后顺序排序
        date_dirs = sorted(date_dirs)
        for dirname in date_dirs:
            result = self.process_directory(dirname=dirname)
            if result != 0:
                return result
        # 跑零售的差异分析
        conf_file = os.path.join(path, "production.yml")
        if os.path.exists(conf_file) and os.path.isfile(conf_file):
            os.chdir(path)
            result = diff_main()
            return result
        return 0


def main():
    try:
        state = Runner().run()
    except Exception as e:
        logging.getLogger(__name__).exception('An error occurred.', exc_info=e)
        return 1
    else:
        return state


if __name__ == '__main__':
    main()
