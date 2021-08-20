# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 09:44:36
@LastEditTime: 2021-08-09 15:43:12
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.models.enum import *
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import PageInfo
from seven_cloudapp_frame.models.db_models.ip.ip_info_model import *


class IpBaseModel():
    """
    :description: IP信息基类
    """
    def __init__(self, context):
        self.context = context
    
    def _delete_ip_info_dependency_key(self,act_id):
        """
        :description: 删除ip信息依赖建
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            if act_id:
                redis_init.delete(f"ip_info_list:actid_{act_id}")
        except Exception as ex:
            pass

    def save_ip_info(self, app_id,act_id,ip_id,ip_name,ip_pic,show_pic,sort_index,is_release):
        """
        :description: 保存ip信息
        :param app_id：应用标识
        :param act_id：活动标识
        :param ip_id: ip标识
        :param ip_name：ip名称
        :param ip_pic：ip图片
        :param show_pic：展示图片
        :param sort_index：排序
        :param is_release：是否发布
        :return
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not app_id or not act_id or not ip_name:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data

        ip_info = None
        is_add = False
        ip_info_model = IpInfoModel(context=self)
        if ip_id > 0:
            ip_info = ip_info_model.get_entity_by_id(ip_id)
            if not ip_info or ip_info.app_id != app_id:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "ip信息不存在"
                return invoke_result_data
            old_ip_info = deepcopy(ip_info)
        if not ip_info:
            is_add = True
            ip_info = IpInfo()
        ip_info.app_id = app_id
        ip_info.act_id = act_id
        ip_info.series_name = ip_name
        ip_info.series_pic = ip_pic
        ip_info.show_pic = show_pic
        ip_info.sort_index = sort_index
        ip_info.is_release = is_release
        ip_info.modify_date = SevenHelper.get_now_datetime()
        if is_add:
            ip_info.create_date = ip_info.modify_date
            ip_info.id = ip_info_model.add_entity(ip_info)
        else:
            ip_info_model.update_entity(ip_info,exclude_field_list="app_id,act_id")
        result = {}
        result["is_add"] = is_add
        result["new"] = ip_info
        result["old"] = old_ip_info
        invoke_result_data.data = result
        self._delete_ip_info_dependency_key(act_id)
        return invoke_result_data

    def get_ip_info_list(self,app_id,act_id,page_size,page_index,order_by="sort_index desc",is_cache=True):
        """
        :description: 获取IP列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :param order_by：排序
        :param is_cache：是否缓存
        :return: list
        :last_editors: HuangJianYi
        """
        condition = "app_id=%s and act_id=%s"
        params = [app_id,act_id]
        if is_cache == True:
            page_list, total = IpInfoModel(context=self).get_cache_dict_page_list(field="*", page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by,params=params,dependency_key=f"ip_info_list:actid_{act_id}",cache_expire=600)
        else:
            page_list, total = IpInfoModel(context=self).get_dict_page_list(field="*", page_index=page_index, page_size=page_size, where=condition, group_by="", order_by=order_by,params=params)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def delete_ip_info(self,app_id,act_id,ip_id):
        """
        :description: 删除ip
        :param app_id：应用标识
        :param act_id：活动标识
        :param ip_id：ip标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        ip_info_model = IpInfoModel(context=self.context)
        ip_info_dict = ip_info_model.get_dict_by_id(ip_id)
        if not ip_info_dict or ip_info_dict["act_id"]!=act_id or ip_info_dict["app_id"]!=app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "ip信息不存在"
            return invoke_result_data
            
        invoke_result_data.success = ip_info_model.del_entity("id=%s", ip_id)
        self._delete_ip_info_dependency_key(act_id)
        return invoke_result_data

    def release_ip_info(self,app_id,act_id,ip_id,is_release):
        """
        :description: ip上下架
        :param app_id：应用标识
        :param act_id：活动标识
        :param ip_id：ip标识
        :param is_release: 是否发布 1-是 0-否
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        ip_info_model = IpInfoModel(context=self.context)
        ip_info_dict = ip_info_model.get_dict_by_id(ip_id)
        if not ip_info_dict or ip_info_dict["act_id"]!=act_id or ip_info_dict["app_id"]!=app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "ip信息不存在"
            return invoke_result_data
            
        invoke_result_data.success = ip_info_model.update_table("is_release=%s", "id=%s", [is_release, ip_id])
        self._delete_ip_info_dependency_key(act_id)
        return invoke_result_data