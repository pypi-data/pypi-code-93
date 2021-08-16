#! /usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import logging
import re

import MySQLdb
from django.db import connections
from ..models.query import SqlBuilder

from ..models.statistic import Statistic
from framework.utils import convert_to_datetime

import settings
from log_def.models import DictDefine
from framework.utils import trace_msg

_logger = logging.getLogger('statistic')

CENTER_CONN = None


def get_center_conn(alias='default'):
    '''获取中央服的mysql连接
    '''
    global CENTER_CONN
    try:
        CENTER_CONN.ping()
    except:
        db_cfg = settings.DATABASES.get(alias, {})
        if db_cfg:
            conf_cfg = {"host"   : db_cfg.get('HOST'),
                        "user"   : db_cfg.get('USER'),
                        "passwd" : db_cfg.get('PASSWORD'),
                        "port"   : int(db_cfg.get('PORT', 3306)),
                        "db"     : db_cfg.get('NAME'),
                        "charset": 'utf8'
                        }
            CENTER_CONN = MySQLdb.connect(**conf_cfg)
    return CENTER_CONN


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


class StatisticBuilder(SqlBuilder):

    def __init__(self, sm, statistic_model, server_model=None):
        self.statistic = statistic_model
        self.server_model = server_model
        self.sm = sm
        super(StatisticBuilder, self).__init__(
                self.statistic.sql, self.sm.params)
        self.prepare_param()

    def prepare_param(self):
        sdate = self.sm.sdate
        edate = self.sm.edate
        if self.sm.use_auto_exec_interval and self.statistic.auto_exec_interval:  # 使用统计间隔,通常是定时任务
            auto_exec_interval = self.statistic.auto_exec_interval
            sdate += datetime.timedelta(days=-auto_exec_interval)

        self.sdate_str = sdate.strftime(self.sm.SDATE_FORMAT)
        self.edate_str = edate.strftime(self.sm.EDATE_FROMAT)

        self.params.update({"sdate": [self.sdate_str]})  # 传开始时间
        self.params.update({"edate": [self.edate_str]})  # 传结束时间
        if self.server_model:
            self.params.update({"server_id": [self.server_model.id]})
            self.params.update(
                    {"game_alias": [self.server_model.alias]})  # 传游戏名

    def query_sql_handle(self):
        '''query_sql_handle 增加获取统计id 使用方法 <<统计名>>
        '''
        if re.search(r'<<\S*>>', self.query_sql):  # 包含<<统计名>>标签
            statistic_names = DictDefine.get_dict_for_key(
                    'statistic_name', reverse=False)
            for k, v in statistic_names.iteritems():
                self.query_sql = self.query_sql.replace('<<%s>>' % v, str(k))
        return super(StatisticBuilder, self).query_sql_handle()


class StatisticExcute(object):
    '''统计执行
    '''

    def __init__(self, query_conn, statistic_analysis, manager):
        self.manager = manager
        self.query_conn = query_conn
        self.statistic_analysis = statistic_analysis

        if self.statistic_analysis.statistic.is_save_center:
            self.center_conn = get_center_conn()  # self.manager.center_conn
        else:
            from ..models import Server

            self.center_conn = Server.get_conn(
                    self.statistic_analysis.server_model.id)

        self.center_conn.autocommit(False)

        self.statistic_analysis.query_sql_handle()
        self.query_sql = self.statistic_analysis.get_query_sql()
        self.save_table_name = self.statistic_analysis.statistic.save_table_name or Statistic.DEFAULT_SAVE_TABLE_NAME

    def start(self):
        if self.query_sql:
            try:
                self.del_old_result()
                has_data = self.insert_new_result()
                self.center_conn.commit()
            except Exception as e:
                self.center_conn.rollback()
                err_msg = trace_msg()
                err_msg = '%s:%s | %s' % (
                        self.statistic_analysis.statistic.name, self.query_sql, err_msg)
                _logger.warn(err_msg)
                raise e

    def insert_new_result(self):
        sql = "INSERT INTO {save_table} SET log_user=unix_timestamp(), log_type='{statistic_id}',f1='{statistic_name}',log_time=%s,log_name=%s,log_sdk_code=%s,log_server=%s,log_channel=%s,log_channel2=%s,log_tag=%s,log_now=%s"
        sql = sql.format(save_table=self.save_table_name, statistic_id=self.statistic_analysis.statistic.id,
                         statistic_name=self.statistic_analysis.statistic.name)
        sql2 = sql + ',log_previous=%s'
        sql3 = sql2 + ',log_result=%s'
        sql4 = sql3 + ',log_data=%s'
        results = self.excute_query()
        cur = self.center_conn.cursor()
        insert_sql = sql
        has_data = False
        for result in results:
            if result:
                row1 = result[0]
                result_length = len(row1)
                if result_length == 9:
                    insert_sql = sql2
                elif result_length == 10:
                    insert_sql = sql3
                elif result_length == 11:
                    insert_sql = sql4

            remove_field = self.statistic_analysis.statistic.remove_field

            if remove_field:
                insert_sql += ",date_time=" + remove_field
            else:
                insert_sql += ",date_time=`log_time`"

            _logger.info(insert_sql)
            cur.executemany(insert_sql, result)
            has_data = True
        return has_data

    def del_old_result(self):
        '''删除旧数据
        '''
        remove_field = self.statistic_analysis.statistic.remove_field
        if not remove_field:
            remove_field = "log_time"
        else:
            remove_field = "date_time"

        sql = "DELETE FROM {save_table} WHERE log_type='{statistic_id}' AND {remove_field}>='{sdate}' AND {remove_field}<='{edate}' "
        sql = sql.format(remove_field=remove_field, save_table=self.save_table_name,
                         statistic_id=self.statistic_analysis.statistic.id,
                         sdate=self.statistic_analysis.sdate_str, edate=self.statistic_analysis.edate_str)

        if self.statistic_analysis.server_model:  # 分服查询
            sql += ' AND log_name="%s" ' % (
                    self.statistic_analysis.server_model.alias)
        cur = self.center_conn.cursor()
        _logger.info(sql)
        cur.execute(sql)
        self.center_conn.commit()

    def excute_query(self, size=50000):
        if self.query_sql:
            cursor = self.query_conn.cursor()
            cursor.execute(self.query_sql)
            while True:
                result = cursor.fetchmany(size)
                if not result:
                    break
                yield result
        else:
            yield ()


class StatisticManager(object):
    SDATE_FORMAT = '%Y-%m-%d 00:00:00'  # 开始时间的格式
    EDATE_FROMAT = '%Y-%m-%d 23:59:59'  # 结束时间的格式

    def __init__(self, sdate, edate, statistic_ids, server_ids=[], use_auto_exec_interval=False):
        self.statistics = Statistic.objects.filter(
                id__in=statistic_ids) if statistic_ids else Statistic.objects.all()
        self.statistics = self.statistics.filter(is_auto_execute=1)
        self.statistic_ids = [str(x) for x in statistic_ids if x]
        # todo
        from ..models import Server
        self.servers = Server.objects.filter(
                id__in=server_ids) if server_ids else Server.objects.filter(status__gte=0)
        self.center_statistic_objs = []
        self.server_statistic_objs = []
        self.sdate = convert_to_datetime(sdate)
        self.edate = convert_to_datetime(edate)
        self.use_auto_exec_interval = use_auto_exec_interval
        self.params = {}
        self.center_conn = get_center_conn()
        self.error_server_ids = []

        for statistic in self.statistics:
            if statistic.is_center():
                self.center_statistic_objs.append(statistic)
            else:
                self.server_statistic_objs.append(statistic)

    def start_update(self):
        err_msgs = []
        _logger.info('服务器数:%s 统计项目数:%s 开始' %
                     (len(self.servers), len(self.statistics)))
        server_error_msgs, err_servers, err_statistic = self.update_server_statistic()
        center_error_msgs, err_center_statistic = self.update_center_statistic()

        err_msgs = server_error_msgs + center_error_msgs

        _logger.info('服务器数:%s 统计项目数:%s 结束  ' %
                     (len(self.servers), len(self.statistics)))
        return err_msgs, set(err_servers), set(err_statistic + err_center_statistic)

    def update_server_statistic(self):
        '''更新分服的统计
        '''
        err_servers = []
        err_statistic = []
        err_msgs = []
        for server_model in self.servers:
            try:
                self.server_count = 0
                # 查询读从库
                query_conn = server_model.mysql_conn(from_read_db=True)
                for statisti_model in self.server_statistic_objs:
                    try:
                        statistic_analysis = StatisticBuilder(
                                self, statisti_model, server_model)
                        statistic_excute = StatisticExcute(
                                query_conn, statistic_analysis, self)
                        statistic_excute.start()
                    except:
                        err_msg = trace_msg()
                        err_msg = '服务器 %s(%s) 统计名(%s) 错误:%s' % (server_model.name, server_model.id,
                                                                statisti_model.name, err_msg
                                                                )
                        _logger.warn(err_msg)
                        err_msgs.append(err_msg)
                        err_servers.append(server_model.id)
                        err_statistic.append(statisti_model.id)
                query_conn.close()
            except:
                for statisti_model in self.server_statistic_objs:
                    err_statistic.append(statisti_model.id)
                err_servers.append(server_model.id)
                err_msg = trace_msg()
                err_msg = '服务器 %s(%s) 错误:%s' % (
                        server_model.name, server_model.id, err_msg)
                err_msgs.append(err_msg)
                _logger.warn(err_msg)
                self.error_server_ids.append(server_model.id)

        for ss in self.server_statistic_objs:
            ssa = StatisticBuilder(self, ss)
            # 检查mysql链接是否失效
            close_old_connections()
            new_ss = Statistic.objects.get(id=ss.id)
            new_ss.last_exec_time = datetime.datetime.now()
            new_ss.result_data = '[%s - %s]:(%s)' % (
                    ssa.sdate_str, ssa.edate_str, self.error_server_ids)
            new_ss.save()
        return err_msgs, err_servers, err_statistic

    def update_center_statistic(self):
        ''' 更新中央后台的统计
        '''
        err_statistic = []
        err_msgs = []
        self.server_count = 0
        for statisti_model in self.center_statistic_objs:
            try:
                statistic_analysis = StatisticBuilder(
                        self, statisti_model, None)
                query_conn = get_center_conn()
                statistic_excute = StatisticExcute(
                        query_conn, statistic_analysis, self)
                statistic_excute.start()
            except:
                err_statistic.append(statisti_model.id)
                err_msg = trace_msg()
                err_msg = '中央统计 统计名(%s) 错误:%s' % (statisti_model.name, err_msg)
                _logger.warn(err_msg)
                err_msgs.append(err_msg)

        for ss in self.center_statistic_objs:
            # 检查mysql链接是否失效
            close_old_connections()
            ssa = StatisticBuilder(self, ss)
            new_ss = Statistic.objects.get(id=ss.id)
            new_ss.last_exec_time = datetime.datetime.now()
            new_ss.result_data = '[%s - %s]' % (ssa.sdate_str, ssa.edate_str)
            new_ss.save()
        return err_msgs, err_statistic
