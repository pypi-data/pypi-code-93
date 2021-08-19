# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-02 13:51:10
@LastEditTime: 2021-08-02 13:57:31
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.models.app_base_model import *
from seven_cloudapp_frame.handlers.frame_base import *


class AppExpireHandler(TaoBaseHandler):
    """
    :description: 获取小程序是否过期未续费
    """
    def get_async(self):
        """
        :description: 获取小程序是否过期未续费
        :return info
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id

        app_base_model = AppBaseModel(context=self)
        invoke_result_data = app_base_model.get_app_expire(app_id)
        if invoke_result_data.success ==False:
            return self.response_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
        return self.response_json_success(invoke_result_data.data)