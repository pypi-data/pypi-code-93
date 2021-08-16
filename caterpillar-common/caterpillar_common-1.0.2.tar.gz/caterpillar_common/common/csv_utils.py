import csv
import logging
from pathlib import Path

from caterpillar_common.common.log import logger

log = logging.getLogger("caterpillar_common")


class CSV(object):
    def __init__(self, csv_file=""):
        self.__csv_file = csv_file

    def write_row(self, data, head="", mode="a+"):
        if isinstance(data, dict):
            try:
                is_empty=self.is_empty()
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.DictWriter(f, fieldnames=head or data.keys())
                    if is_empty:
                        csv_writer.writeheader()
                    csv_writer.writerow(data)
            except Exception as e:
                log.error(
                    f"向csv文件写入一行字典数据失败，csv文件为：{self.__csv_file}, 行数据为：{data}, 写入模式为：{mode}，标题信息为：{head}。报错信息如下：{str(e)}")
        else:
            try:
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerow(data)
            except Exception as e:
                log.error(
                    f"向csv文件写入一行列表数据失败，csv文件为：{self.__csv_file}, 行数据为：{data}, 写入模式为：{mode}。报错信息如下：{str(e)}")

    def write_rows(self, datas, head="", mode="a+"):
        if len(datas) == 0:
            return
        if isinstance(datas[0],dict):
            try:
                is_empty=self.is_empty()
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.DictWriter(f, fieldnames=head or list(datas[0].keys()))
                    if is_empty:
                        csv_writer.writeheader()
                    csv_writer.writerows(datas)
            except Exception as e:
                log.error(
                    f"向csv文件写入多行字典数据失败，csv文件为：{self.__csv_file}, 第一行数据为：{datas[0]}, 写入模式为：{mode}，标题信息为：{head}。报错信息如下：{str(e)}")
        else:
            try:
                with open(self.__csv_file, mode, encoding="utf8", newline="") as f:
                    csv_writer = csv.writer(f)
                    csv_writer.writerows(datas)
            except Exception as e:
                log.error(
                    f"向csv文件写入多行列表数据失败，csv文件为：{self.__csv_file}, 行数据为：{datas}, 写入模式为：{mode}。报错信息如下：{str(e)}")

    def get_rows(self,is_dict=False):
        try:
            if is_dict:
                with open(self.__csv_file,"r",encoding="utf8",newline="") as f:
                    return list(csv.DictReader(f))
            else:
                with open(self.__csv_file,"r",encoding="utf8",newline="") as f:
                    return list(csv.reader(f))
        except Exception as e:
            log.error(f"获取csv文件内容时出错了，错误信息为：{str(e)}")
            return []

    def is_empty(self):
        if not Path(self.__csv_file).exists():
            return True
        return len(self.get_rows())==0
