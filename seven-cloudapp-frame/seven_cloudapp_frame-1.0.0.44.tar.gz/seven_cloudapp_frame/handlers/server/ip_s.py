# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 11:03:56
@LastEditTime: 2021-08-18 18:12:20
@LastEditors: HuangJianYi
@Description: 
"""

from seven_cloudapp_frame.models.ip_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *
from seven_cloudapp_frame.models.enum import *


class SaveIpInfoHandler(TaoBaseHandler):
    """
    :description: 保存IP信息
    """
    @filter_check_params("act_id,ip_name,ip_pic")
    def get_async(self):
        """
        :description: 保存IP信息
        :param app_id：应用标识
        :param act_id：活动标识
        :param ip_id: ip标识
        :param ip_name：ip名称
        :param ip_pic：ip图片
        :param show_pic：展示图片
        :param sort_index：排序
        :param is_release：是否发布
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        ip_id = int(self.get_param("ip_id", 0))
        act_id = int(self.get_param("act_id", 0))
        ip_name = self.get_param("ip_name")
        ip_pic = self.get_param("ip_pic")
        show_pic = self.get_param("show_pic")
        sort_index = int(self.get_param("sort_index", 0))
        is_release = int(self.get_param("is_release", 1))

        ip_base_model = IpBaseModel(context=self)
        invoke_result_data = ip_base_model.save_ip_info(app_id, act_id, ip_id, ip_name, ip_pic, show_pic, sort_index, is_release)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        if invoke_result_data.data["is_add"] == True:
            # 记录日志
            self.create_operation_log(OperationType.add.value, invoke_result_data.data["new"].__str__(), "SaveIpInfoHandler", None, self.json_dumps(invoke_result_data.data["new"]), self.get_taobao_param().open_id, self.get_taobao_param().user_nick)
        else:
            self.create_operation_log(OperationType.update.value, invoke_result_data.data["new"].__str__(), "SaveIpInfoHandler", self.json_dumps(invoke_result_data.data["old"]), self.json_dumps(invoke_result_data.data["new"]), self.get_taobao_param().open_id, self.get_taobao_param().user_nick)

        self.response_json_success(invoke_result_data.data["new"].id)


class IpInfoListHandler(TaoBaseHandler):
    """
    :description: 获取ip列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取ip列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        self.response_json_success(IpBaseModel(context=self).get_ip_info_list(app_id, act_id, page_size, page_index,is_cache=False))


class DeleteIpInfoHandler(TaoBaseHandler):
    """
    :description: 删除ip
    """
    @filter_check_params("ip_id")
    def get_async(self):
        """
        :description: 删除ip
        :param app_id：应用标识
        :param act_id：活动标识
        :param ip_id: ip标识
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        ip_id = int(self.get_param("ip_id", 0))

        ip_base_model = IpBaseModel(context=self)
        invoke_result_data = ip_base_model.delete_ip_info(app_id, act_id, ip_id)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

        self.create_operation_log(OperationType.delete.value, "ip_info_tb", "DeleteIpInfoHandler", None, ip_id)

        self.response_json_success()


class ReleaseIpInfoHandler(TaoBaseHandler):
    """
    :description: 上下架ip
    """
    @filter_check_params("ip_id")
    def get_async(self):
        """
        :description: 上下架ip
        :param app_id：应用标识
        :param act_id：活动标识
        :param ip_id: ip标识
        :param is_release: 是否发布 1-是 0-否
        :return: response_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        act_id = int(self.get_param("act_id", 0))
        ip_id = int(self.get_param("ip_id", 0))
        is_release = int(self.get_param("is_release", 0))

        ip_base_model = IpBaseModel(context=self)
        invoke_result_data = ip_base_model.release_ip_info(app_id, act_id, ip_id, is_release)
        if invoke_result_data.success == False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)

        self.response_json_success()
