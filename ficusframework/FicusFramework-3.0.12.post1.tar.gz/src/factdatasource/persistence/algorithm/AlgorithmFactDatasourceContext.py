#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import logging

from factdatasource.execptions import NotSupportedFDException, FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext
from libs.utils import get_algo_abs_path, delete_file
from munch import Munch
from api.model.AlgoOutWrapper import AlgoOutWrapper
import os

log = logging.getLogger('Ficus')


class AlgorithmDatasourceContext(AbstractFactDatasourceContext):

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        fd = self.fd()
        file_name = get_algo_abs_path(fd.site, fd.connection, fd.target)
        if not os.path.exists(file_name):
            return 0
        elif os.path.isfile(file_name):
            return 1
        else:
            # 只计算一层
            return len(os.listdir(file_name))

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        return self.size() == 0

    def collect(self, size: int):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :return: list
        """
        raise NotSupportedFDException('algorithm不支持该操作')

    def collect_conditions(self, size: int, condition_groups: list):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :param condition_groups: 查询条件
        :return: list
        """
        raise NotSupportedFDException('algorithm不支持该操作')

    def query(self, query: str, parameters: dict = None):
        """
        使用查询语句查询数据
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        raise NotSupportedFDException('algorithm不支持该操作')

    def inserts(self, result_list: list):
        """
        insert是重新写入
        :param result_list: 要保存的数据
        :return:
        """
        return self.__save_or_update(result_list, 'insert')

    def updates(self, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        return self.__save_or_update(result_list, 'update')

    def inserts_or_updates(self, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        return self.__save_or_update(result_list, 'saveOrUpdate')

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        # 消息可能是有顺序的,因此先不并发
        raise NotSupportedFDException('algorithm不支持该操作')

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        # 消息可能是有顺序的,因此先不并发
        raise NotSupportedFDException('algorithm不支持该操作')

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        # 消息可能是有顺序的,因此先不并发
        raise NotSupportedFDException('algorithm不支持该操作')

    def delete_all(self):
        """
        清空数据
        :return:
        """
        fd = self.fd()
        delete_file(get_algo_abs_path(fd.site, fd.connection, ''))

    def delete(self, query: str):
        """
        query默认是个文件名称，删除这个fd配置路径下的该文件
        :return:
        """
        fd = self.fd()
        delete_file(get_algo_abs_path(fd.site, fd.connection, query))

    def delete_conditions(self, condition_groups: list):
        raise NotSupportedFDException('algorithm不支持该操作')

    def __save_or_update(self, result_list: list, method: str):
        if not result_list:
            return []
        fd = self.fd()
        results = []
        result_one = result_list[0]
        if isinstance(result_one, dict) and 'subPath' in result_one.keys():
            # 说明是AlgoOutWrapper.WITH传进来的
            for serializable in result_list:
                try:
                    if not isinstance(serializable, dict):
                        serializable = vars(serializable)
                    data = serializable.get('t')
                    sub_path = serializable.get('subPath')
                    abs_sub_path = get_algo_abs_path(fd.site, fd.connection, sub_path)
                    self.__validate_file(method, abs_sub_path)
                    with open(abs_sub_path, 'ab+') as f:
                        f.write(self.__getByteData(data))
                    results.append(Munch({"success": True}))
                except Exception as e:
                    error = 'AlgorithmFactDatasourceContext插入时，文件写入报错'
                    log.error(error, e)
                    results.append(Munch({"success": False, "error": f'AlgorithmFactDatasourceContext插入时，文件写入报错，路径是{abs_sub_path}',
                                          "content": serializable}))
        else:
            # 说明是普通模式
            if not fd.target:
                raise FDExecuteException('fd的target为空，不是文件类型，不允许插入')
            path = get_algo_abs_path(fd.site, fd.connection, fd.target)
            self.__validate_file(method, path)
            for serializable in result_list:
                try:
                    with open(path, 'ab+') as f:
                        f.write(self.__getByteData(serializable))
                    results.append(Munch({"success": True}))
                except Exception as e:
                    error = 'AlgorithmFactDatasourceContext插入时，文件写入报错'
                    log.error(error, e)
                    results.append(Munch({"success": False, "error": f'AlgorithmFactDatasourceContext插入时，文件写入报错，路径是{path}',
                                          "content": serializable}))
        return results

    def __validate_file(self, method: str, path: str):
        if not os.path.exists(path):
            if 'update' == method:
                raise FDExecuteException(f'{path}路径的文件不存在，无法更新')
            parent_dir = os.path.abspath(os.path.dirname(path))
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            f = open(path, 'w')
            f.close()
        else:
            # 只有插入的是新建文件，需要删除旧文件
            if 'insert' == method:
                os.remove(path)
                f = open(path, 'w')
                f.close()

    def __getByteData(self, data):
        import json
        if isinstance(data, dict):
            return json.dumps(data).encode()
        elif isinstance(data, str):
            return data.encode()