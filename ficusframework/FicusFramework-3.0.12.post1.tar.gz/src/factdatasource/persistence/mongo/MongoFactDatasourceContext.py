#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# Author: lvbiao
# Created on 2019/1/21
import json
import logging

from bson import SON
from munch import Munch

from api.exceptions import IllegalArgumentException
from api.model.Page import Page
from factdatasource.dao.FactDatasource import customer_dao_context_holder as costomer_context
from factdatasource.dao.mongo.MongoDatasourceDao import MongoDatasourceDao
from factdatasource.execptions import FDExecuteException
from factdatasource.persistence.AbstractFactDatasourceContext import AbstractFactDatasourceContext

log = logging.getLogger('Ficus')


class MongoFactDatasourceContext(AbstractFactDatasourceContext):

    @property
    def dao(self) -> MongoDatasourceDao:
        return MongoDatasourceDao.instance()

    def size(self):
        """
        返回数据总长度
        :return: 数据条数:long
        """
        source_name = self.fd().get_source_name()
        target = self.fd().get_target_with_schema()
        try:
            costomer_context.set_source(source_name)
            result = self.dao.count_documents(target)
            size = 0 if result is None else result
            return size
        except Exception as e:
            error = f'事实库{source_name}执行size操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def is_empty(self):
        """
        返回是否存在数据
        :return: boolean
        """
        source_name = self.fd().get_source_name()
        target = self.fd().get_target_with_schema()
        try:
            costomer_context.set_source(source_name)
            result = self.dao.count_documents(target)
            size = 0 if result is None else result
            return size <= 0
        except Exception as e:
            error = f'事实库{source_name}执行is_empty操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def collect(self, size: int):
        """
        返回指定条数的数据
        TODO 返回结果中ObjectId暂时未进行处理
        :param size: 返回的条数
        :return: list
        """
        source_name = self.fd().get_source_name()
        target = self.fd().get_target_with_schema()
        try:
            costomer_context.set_source(source_name)
            size = size if size else 0
            result = self.dao.find(target, {}, limit=size)
            return result
        except Exception as e:
            error = f'事实库{source_name}执行collect操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def collect_conditions(self, size: int, condition_groups: list):
        """
        返回指定条数的数据
        :param size: 返回的条数
        :param condition_groups: 查询条件
        :return: list
        """
        # TODO 这里需要构造mongo的bson,python没有对象方式的构建,需要自己拼json
        return None

    def query(self, query: str, parameters: dict = None):
        """
        使用查询语句查询数据
        needCount_参数的功能暂时只有普通查询会支持,map_reduce查询不会支持分页
        :param query: 查询语句
        :param parameters: 查询参数
        :return: Page
        """
        source_name = self.fd().get_source_name()

        if not query or not isinstance(query, str):
            raise IllegalArgumentException(f'事实库{source_name}执行query操作发生异常, 查询参数query：{query} 错误。')

        source_name = self.fd().get_source_name()
        target = self.fd().get_target_with_schema()

        page = None
        if parameters and 'pageNum_' in parameters.keys() and 'pageSize_' in parameters.keys():
            # 需要分页的
            param = {
                'pageNum': parameters.get('pageNum_'),
                'pageSize': parameters.get('pageSize_'),
                'needCount': parameters.get('needCount_') if parameters.get('needCount_') else False
            }
            page = Page(**param)

        # 参数占位符处理
        query = self._fd_placeholder_replace(query, parameters)

        # 处理SQL空格
        query = query.strip()

        try:
            log.debug(f'事实库{source_name}执行query操作SQL：{query}')
            costomer_context.set_source(source_name)

            if query.startswith('{') and query.endswith('}'):

                query = json.loads(query)

                if 'map' in query and 'reduce' in query and 'mapreduce' in query:
                    # 说明是map_reduce方式的函数
                    query_result = self._execute_map_reduce(target, query)
                    return Page.no_page(query_result)
                else:
                    # TODO 普通查询功能比较单一，是否需要进行扩展， 现在只支持filter,对于sort，limit,skip等没有支持
                    page = self._execute_normal_query(target, query, page)
                    return page
            elif query.startswith('[') and query.endswith(']'):
                query = json.loads(query)
                page = self._execute_aggregate_query(target, query, page)
                return page
            else:
                raise FDExecuteException(f'事实库{source_name}执行query操作查询语句错误，SQL：{query}')
        except Exception as e:
            error = f'事实库{source_name}执行query操作SQL：{query} 发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def _single_thread_inserts(self, table: str, result_list: list):
        """
        批量保存数据,要求list里面的字段和数据库里面的字段一一对应
        :param result_list: 要保存的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        rrr=[]
        try:
            costomer_context.set_source(source_name)
            self.dao.insert(table, result_list)
            rrr.append(Munch({"success": True}))
        except Exception as e:
            error = f'事实库{source_name}执行inserts操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()
        return rrr

    def _single_thread_updates(self, table: str, result_list: list):
        """
        批量更新数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要修改的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        rrr=[]
        try:
            costomer_context.set_source(source_name)
            primary_keys = self.get_primary_keys()
            for result in result_list:
                if not isinstance(result, dict):
                    result = vars(result)

                primary_values = self.get_primary_values(primary_keys, result)
                if not primary_values:
                    # 没有id字段，放弃该数据
                    log.warning(f'事实库{source_name}执行updates操作时未配置主键字段,放弃该数据的更新：{result}')
                    rrr.append(Munch({"success": False, "error": f'事实库{source_name}执行updates操作时未配置主键字段,放弃该数据的更新', "content": result}))
                    continue
                self.dao.update_one(table, primary_values, result)
                rrr.append(Munch({"success": True}))
        except Exception as e:
            error = f'事实库{source_name}执行updates操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()
        return rrr

    def _single_thread_inserts_or_updates(self, table: str, result_list: list):
        """
        批量saveOrUpdate数据,数据,要求list里面的字段和数据库里面的字段一一对应
        采用ByPrimaryKeySelective的方式,也就是主键必填,其他的字段非空就是要修改的
        :param result_list: 要添加或者需要修改的数据
        :return:
        """
        source_name = self.fd().get_source_name()
        rrr=[]
        try:
            costomer_context.set_source(source_name)
            primary_keys = self.get_primary_keys()
            for result in result_list:
                if not isinstance(result, dict):
                    result = vars(result)

                primary_values = self.get_primary_values(primary_keys, result)
                if not primary_values:
                    # 没有id字段,直接尝试插入
                    self.dao.insert(table, [result])
                else:
                    self.dao.update_one(table, primary_values, result,  upsert=True)
                rrr.append(Munch({"success": True}))
        except Exception as e:
            error = f'事实库{source_name}执行updates操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()
        return rrr

    def delete_all(self):
        """
        清空数据
        :return:
        """
        source_name = self.fd().get_source_name()
        target = self.fd().get_target_with_schema()
        try:
            costomer_context.set_source(source_name)
            self.dao.drop(target)
        except Exception as e:
            error = f'事实库{source_name}执行delete_all操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def delete(self, query: str):
        """
        根据删除语句删除数据,query是mongo查询语句
        :param query:
        :return:
        """
        source_name = self.fd().get_source_name()
        target = self.fd().get_target_with_schema()
        try:
            costomer_context.set_source(source_name)
            query = json.loads(query)
            self.dao.delete_many(target, query)
        except Exception as e:
            error = f'事实库{source_name}执行delete操作发生异常, {str(e)}'
            log.error(error)
            raise FDExecuteException(error)
        finally:
            costomer_context.clear_source()

    def delete_conditions(self, condition_groups: list):
        """
        根据删除条件,构造删除语句
        :param condition_groups:
        :return:
        """
        # TODO 这里需要构造mongo的bson,python没有对象方式的构建,需要自己拼json

    # region 查询结构构造
    def _execute_map_reduce(self, target: str, query: dict) -> list:
        """
        map_reduce 查询构造结果
        :param target:
        :param query:
        :return:
        """
        kwargs = query.copy()

        t = kwargs.pop('mapreduce')
        target = t if t else target

        map = kwargs.pop('map')
        reduce = kwargs.pop('reduce')
        if 'out' in kwargs.keys():
            out = kwargs.pop('out')
        else:
            out = SON([('inline', 1)])
        kwargs['full_response'] = True
        query_result = self.dao.map_reduce(target, map, reduce, out, **kwargs)
        if 'results' in query_result:
            return query_result.get('results')
        elif 'result' in query_result:
            return [query_result.get('result')]

    def _execute_normal_query(self, target: str, query: dict, page: Page) -> Page:
        """
        普通查询构造结果
        :param target:
        :param query:
        :param page:
        :return:  page
        """
        # 普通查询
        kwargs = {
            'filter': query
        }
        if page:
            kwargs['skip'] = page.start_row
            kwargs['limit'] = page.pageSize
        query_result = self.dao.find(target, **kwargs)

        if page:
            total = None
            if page.need_count():
                total = self.dao.count_documents(target, filter=query)
            page.set_result(query_result, total)
        else:
            page = Page.no_page(query_result)
        return page

    def _execute_aggregate_query(self, target: str, query: list, page: Page) -> Page:
        if page:
            query.append({"$skip": page.start_row})
            query.append({"$limit": page.pageSize})

        query_result = self.dao.aggregate(target, query)

        if page:
            # TODO 这里暂时不支持count查询
            page.set_result(query_result, None)
        else:
            page = Page.no_page(query_result)
        return page

    # endregion
