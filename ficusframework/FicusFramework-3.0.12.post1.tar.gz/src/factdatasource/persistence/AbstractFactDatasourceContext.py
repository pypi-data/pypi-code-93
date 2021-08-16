#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import math
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from api.exceptions import IllegalArgumentException
from api.model import MetaModelTransform
from api.model.FactDatasource import FactDatasource
from factdatasource.FactDatasourceContext import FactDatasourceContext
from factdatasource.execptions import DatasourceNotFoundException
from factdatasource.transformer import TransformerContext
from libs.utils import str_placeholder_replace


class AbstractFactDatasourceContext(FactDatasourceContext):
    # 默认的分片大小
    default_partition_size = 200
    # 多主键值的连接符
    PRIMARY_CONNECT_STRING = '_'
    # 使用统一的线程池来管理
    __fd_thread_pool = ThreadPoolExecutor(max_workers=20, thread_name_prefix='ficus-fd-')

    def __init__(self, fact_datasource: FactDatasource):
        self.fact_datasource = fact_datasource

    def _fd_placeholder_replace(self, value: str, value_map: dict):
        """
        fd参数的占位符处理
        处理替换${}和#{}两种占位符
        :param value:
        :param value_map:
        :return:
        """
        if not isinstance(value, str):
            raise IllegalArgumentException('占位符处理参数类型错误，value只能为str.')
        if not value_map:
            return value
        value = str_placeholder_replace('${', '}', value, value_map)
        value = str_placeholder_replace('#{', '}', value, value_map)
        return value

    def fd(self) -> FactDatasource:
        if not self.fact_datasource:
            raise DatasourceNotFoundException('未配置数据源')
        return self.fact_datasource

    def inserts(self, result_list: list) -> list:
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        if not result_list:
            return None
        if not isinstance(result_list, list):
            result_list = [result_list]

        table = self.fd().get_target_with_schema()

        partition = self._compute_and_partition_datas(result_list)

        if len(partition) == 1:
            return self._proxy_single_thread_inserts(table, result_list)
        else:
            all_tasks = [self.__fd_thread_pool.submit(self._proxy_single_thread_inserts, table, data) for data in
                         partition]
            wait(all_tasks, return_when=ALL_COMPLETED)
            result = []
            for task in all_tasks:
                result.extend(task.result())
            return result

    def updates(self, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        if not result_list:
            return
        if not isinstance(result_list, list):
            result_list = [result_list]

        table = self.fd().get_target_with_schema()

        partition = self._compute_and_partition_datas(result_list)

        if len(partition) == 1:
            return self._proxy_single_thread_updates(table, result_list)
        else:
            all_tasks = [self.__fd_thread_pool.submit(self._proxy_single_thread_updates, table, data) for data in
                         partition]
            wait(all_tasks, return_when=ALL_COMPLETED)
            result = []
            for task in all_tasks:
                result.extend(task.result())
            return result

    def inserts_or_updates(self, result_list: list):
        """
        批量saveOrUpdate数据,,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        if not result_list:
            return
        if not isinstance(result_list, list):
            result_list = [result_list]

        table = self.fd().get_target_with_schema()

        partition = self._compute_and_partition_datas(result_list)

        if len(partition) == 1:
            return self._proxy_single_thread_inserts_or_updates(table, result_list)
        else:
            all_tasks = [self.__fd_thread_pool.submit(self._proxy_single_thread_inserts_or_updates, table, data) for
                         data in
                         partition]
            wait(all_tasks, return_when=ALL_COMPLETED)
            result = []
            for task in all_tasks:
                result.extend(task.result())
            return result

    def _proxy_single_thread_inserts(self, table: str, result_list: list) -> list:
        self._execute_model_field_transform(result_list)
        return self._single_thread_inserts(table, result_list)

    @abstractmethod
    def _single_thread_inserts(self, table: str, result_list: list) -> list:
        """单线程insert数据"""

    def _proxy_single_thread_updates(self, table: str, result_list: list) -> list:
        self._execute_model_field_transform(result_list)
        return self._single_thread_updates(table, result_list)

    @abstractmethod
    def _single_thread_updates(self, table: str, result_list: list) -> list:
        """单线程update数据"""

    def _proxy_single_thread_inserts_or_updates(self, table: str, result_list: list) -> list:
        self._execute_model_field_transform(result_list)
        return self._single_thread_inserts_or_updates(table, result_list)

    @abstractmethod
    def _single_thread_inserts_or_updates(self, table: str, result_list: list) -> list:
        """单线程upsert数据"""

    def _compute_and_partition_datas(self, data: list) -> list:
        """
        计算,并尽量均分的分片 数据小于 default_partition_size 就不分片了
        :param data:
        :return: list<result_list>
        """
        if not data:
            return None

        if len(data) <= self.default_partition_size:
            return [data]
        # 共分多少片
        n = math.ceil(len(data) / self.default_partition_size)
        # 每片多少个
        num = math.ceil(len(data) / n)
        return [data[i:i + num] for i in range(0, len(data), num)]

    def _execute_model_field_transform(self, result_list):
        """
        字段转换相关
        :param result_list:
        :return:
        """
        if result_list is None or len(result_list) == 0:
            return

        has_transform_meta_model_fields = self._need_transform_model_field()

        if has_transform_meta_model_fields is None or len(has_transform_meta_model_fields) == 0:
            return

        # 说明是需要进行字段转换的
        for serializable in result_list:
            self._inner_execute_model_field_transform(serializable, has_transform_meta_model_fields)

    def _need_transform_model_field(self):
        """
        判断是否需要进行模型字段的转换
        先每一次都判断一次,以后可能再使用缓存
        :return: Map<MetaModelField,List<MetaModelTransform>>
        """
        model = self.fd().model
        if model is None:
            return None

        fields = model.fields
        if fields is None or len(fields) == 0:
            return None
        result = {}
        for field in fields:
            transforms = MetaModelTransform.init_transform_by_field(field.id)
            if transforms is not None:
                result[field] = transforms

        return result

    def _inner_execute_model_field_transform(self, serializable, has_transform_meta_model_fields):
        """
        转换字段
        :param serializable:
        :param has_transform_meta_model_fields:
        :return:
        """

        if serializable is None:
            return

        if isinstance(serializable, list) or isinstance(serializable, set):
            # array或list类型
            for o in serializable:
                self._inner_execute_model_field_transform(o, has_transform_meta_model_fields)
        else:

            for meta_model_field, transforms in has_transform_meta_model_fields.items():
                # 这里是要写入数据库的值
                value = serializable[meta_model_field.fieldName] if meta_model_field.fieldName in serializable else None

                for transform in transforms:
                    transformerParams: dict = transform.params

                    tmp = {meta_model_field.fieldName: value}

                    # 补充关联的字段
                    if transformerParams is not None and "__referenceFields__" in transformerParams:
                        referenceFields: str = transformerParams["__referenceFields__"]
                        if referenceFields is not None and "" != referenceFields:
                            split = referenceFields.split(",")
                            for s in split:
                                if s == "":
                                    continue
                                tmp[s] = serializable[s] if s in serializable else None

                    # 执行转换
                    transformer = TransformerContext.get_transformer(transform)
                    if transformer is not None:
                        objectMap: dict = transformer.transform_field(tmp, transformerParams, meta_model_field)
                        for key, value in objectMap.items():
                            serializable[key] = value
                            tmp[key] = value

    def get_primary_keys(self) -> list:
        """
        获取主键列表
        1. 通过fd中配置模型获取主键列表
        2. 如果没有设置模型，则默认使用id作为主键
        :return:
        """
        fd = self.fd()
        result = list()
        if fd and fd.model and fd.model.fields:
            for field in fd.model.fields:
                if field.primaryKey == 1:
                    # 这里表示这个字段设置的是主键
                    result.append(field.fieldName)

        if not result:
            # 如果没有配置主键，这里兼容老版本，设置id为默认主键
            result.append('id')
        return result

    def get_primary_values(self, primary_keys: list, values: dict):
        """
        根据主键列表的key返回一个包含所有主键的dict
        :param primary_keys:
        :param values:
        :return:
        """
        if not primary_keys or not values:
            return None

        primary_keys = primary_keys.copy()
        # 存一份小写数据，避免每次都遍历找
        values_lower = None

        primary_dict = dict()
        for key in primary_keys:
            v = values.get(key)
            if v is None:
                if not values_lower:
                    values_lower = {str(k).lower(): v for k, v in values.items()}
                # 没有找到，不区分大小写再找一次
                v = values_lower.get(key.lower())
            if v is None:
                return None
            primary_dict[key] = v
        return primary_dict

    def get_primary_values_key(self, primary_keys: list, values: dict):
        """
        根据主键列表的字典顺序拼接主键，使用下划线连接，定义的所有主键都不能为空，主键key不区分大小写
        :return:
        """
        if not primary_keys or not values:
            return None

        primary_dict = self.get_primary_values(primary_keys, values)
        if not primary_dict:
            return None
        sort_key = sorted(primary_dict)
        primary_values = list()
        for key in sort_key:
            primary_values.append(str(primary_dict.get(key)))
        return self.PRIMARY_CONNECT_STRING.join(primary_values)
