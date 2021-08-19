# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-26 09:39:08
@LastEditTime: 2021-08-17 15:39:30
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *

from seven_cloudapp_frame.models.db_models.stat.stat_queue_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_report_model import *
from seven_cloudapp_frame.models.db_models.stat.stat_orm_model import *

class StatBaseModel():
    """
    :description: 统计上报基类
    """
    def __init__(self, context):
        self.context = context

    def add_stat(self, app_id, act_id, module_id, user_id, open_id, key_name, key_value, sub_table=None):
        """
        :description: 添加上报
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param key_name：统计key
        :param key_value：统计value
        :param sub_table：分表名称（是否分表由业务方决定）
        :return:
        :last_editors: HuangJianYi
        """
        stat_queue_model = StatQueueModel(sub_table=sub_table, context=self.context)

        stat_queue = StatQueue()
        stat_queue.app_id = app_id
        stat_queue.act_id = act_id
        stat_queue.module_id = module_id
        stat_queue.user_id = user_id
        stat_queue.open_id = open_id
        stat_queue.key_name = key_name
        stat_queue.key_value = key_value
        stat_queue.create_date = SevenHelper.get_now_datetime()
        stat_queue.process_date = SevenHelper.get_now_datetime()
        return stat_queue_model.add_entity(stat_queue)

    def add_stat_list(self, app_id, act_id, module_id, user_id, open_id, key_list_dict, sub_table=None):
        """
        :description: 添加上报
        :param app_id：应用标识
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param user_id：用户标识
        :param open_id：open_id
        :param key_list_dict:键值对字典
        :param sub_table：分表名称（统计队列表是否分表由业务方决定）
        :return:
        :last_editors: HuangJianYi
        """
        stat_queue_model = StatQueueModel(sub_table=sub_table, context=self.context)
        stat_queue_list = []
        for key,value in key_list_dict.items():
            stat_queue = StatQueue()
            stat_queue.app_id = app_id
            stat_queue.act_id = act_id
            stat_queue.module_id = module_id
            stat_queue.user_id = user_id
            stat_queue.open_id = open_id
            stat_queue.key_name = key
            stat_queue.key_value = value
            stat_queue.create_date = SevenHelper.get_now_datetime()
            stat_queue.process_date = SevenHelper.get_now_datetime()
            stat_queue_list.append(stat_queue)
        return stat_queue_model.add_list(stat_queue_list)

    def get_stat_report_list(self,act_id,module_id,start_date,end_date,order_by="sort_index asc"):
        """
        :description: 报表数据列表(表格)
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param order_by：排序
        :return list
        :last_editors: HuangJianYi
        """
        condition = "act_id=%s and module_id=%s"
        params = [act_id,module_id]
        if start_date != "":
            condition += " and create_date>=%s"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(end_date)

        stat_orm_list = StatOrmModel(context=self.context).get_list("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and is_show=1", order_by=order_by, params=[act_id,module_id])
        if len(stat_orm_list)<=0:
            return []
        key_name_s = ','.join(["'%s'" % str(stat_orm.key_name) for stat_orm in stat_orm_list])
        condition += f" and key_name in({key_name_s})"
        stat_report_model = StatReportModel(context=self.context)
        behavior_report_list = stat_report_model.get_dict_list(condition, group_by="key_name", field="key_name,SUM(key_value) AS key_value",params=params)
        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in stat_orm_list]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["value"] = 0
                for behavior_report in behavior_report_list:
                    if behavior_report["key_name"] == orm.key_name:
                        if orm.value_type == 2:
                            data["value"] = behavior_report["key_value"]
                        else:
                            data["value"] = int(behavior_report["key_value"])
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in stat_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["value"] = 0
                        for behavior_report in behavior_report_list:
                            if behavior_report["key_name"] == orm.key_name:
                                if orm.value_type == 2:
                                    data["value"] = behavior_report["key_value"]
                                else:
                                    data["value"] = int(behavior_report["key_value"])
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return common_group_data_list
    
    def get_trend_report_list(self,act_id,module_id,start_date,end_date,order_by="sort_index asc"):
        """
        :description: 报表数据列表(趋势图)
        :param act_id：活动标识
        :param module_id：活动模块标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param order_by：排序
        :return list
        :last_editors: HuangJianYi
        """
        condition = "act_id=%s and module_id=%s"
        params = [act_id,module_id]
        if start_date != "":
            condition += " and create_date>=%s"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(end_date)

        stat_orm_list = StatOrmModel(context=self.context).get_list("((act_id=%s and module_id=%s) or (act_id=0 and module_id=0)) and is_show=1", order_by=order_by, params=[act_id,module_id])
        if len(stat_orm_list)<=0:
            return []
        key_name_s = ','.join(["'%s'" % str(stat_orm.key_name) for stat_orm in stat_orm_list])
        condition += f" and key_name in({key_name_s})"
        stat_report_model = StatReportModel(context=self.context)
        stat_report_list = stat_report_model.get_dict_list(condition, field="key_name,key_value,DATE_FORMAT(create_date,'%%Y-%%m-%%d') AS create_date",params=params)
        date_list = SevenHelper.get_date_list(start_date, end_date)
        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in stat_orm_list]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["value"] = []
                for date_day in date_list:
                    behavior_date_report = {}
                    for behavior_report in stat_report_list:
                        if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                            if orm.value_type != 2:
                                behavior_report["key_value"] = int(behavior_report["key_value"])
                            behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                            break
                    if not behavior_date_report:
                        behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                    data["value"].append(behavior_date_report)
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in stat_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in stat_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["value"] = []
                        for date_day in date_list:
                            behavior_date_report = {}
                            for behavior_report in stat_report_list:
                                if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                                    if orm.value_type != 2:
                                        behavior_report["key_value"] = int(behavior_report["key_value"])
                                    behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                                    break
                            if not behavior_date_report:
                                behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                            data["value"].append(behavior_date_report)
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return common_group_data_list