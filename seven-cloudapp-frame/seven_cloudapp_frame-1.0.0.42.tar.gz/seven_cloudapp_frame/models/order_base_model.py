# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-09 09:24:43
@LastEditTime: 2021-08-09 17:53:01
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.seven_model import *

from seven_cloudapp_frame.models.db_models.prize.prize_order_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_frame.models.db_models.tao.tao_pay_order_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *


class OrderBaseModel():
    """
    :description: 订单模块基类
    """
    def __init__(self, context):
        self.context = context
    
    
    def _delete_prize_order_dependency_key(self,act_id):
        """
        :description: 删除订单依赖建
        :param act_id: 活动标识
        :return: 
        :last_editors: HuangJianYi
        """
        try:
            redis_init = SevenHelper.redis_init()
            if act_id:
                redis_init.delete(f"prize_order_list:actid_{act_id}")
        except Exception as ex:
            pass

    def get_prize_order_list(self,app_id,act_id,user_id,open_id,nick_name,order_no,real_name,telephone,adress,order_status,create_date_start,create_date_end,page_size=20,page_index=0,order_by="id desc",field="*",is_search_roster=False,is_cache=True):
        """
        :description: 用户奖品订单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param open_id：open_id
        :param order_no：订单号
        :param nick_name：用户昵称
        :param real_name：用户名字
        :param telephone：联系电话
        :param adress：收货地址
        :param order_status：订单状态（-1未付款-2付款中0未发货1已发货2不予发货3已退款4交易成功）
        :param create_date_start：订单创建时间开始
        :param create_date_end：订单创建时间结束
        :param page_size：页大小
        :param page_index：页索引
        :param order_by：排序
        :param field：查询字段
        :param is_search_roster：是否查询订单关联中奖记录
        :param is_cache：是否缓存
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        condition = "app_id=%s and act_id=%s"
        params = [app_id,act_id]
        page_info = PageInfo(page_index, page_size, 0, [])
        
        if not app_id or not act_id:
            return page_info
        if user_id:
            condition += " AND user_id=%s"
            params.append(user_id)
        if open_id:
            condition += " AND open_id=%s"
            params.append(open_id)
        if order_no:
            condition += " AND order_no=%s"
            params.append(order_no)
        if nick_name:
            condition += " AND user_nick=%s"
            params.append(nick_name)
        if real_name:
            condition += " AND real_name=%s"
            params.append(real_name)
        if telephone:
            condition += " AND telephone=%s"
            params.append(telephone)
        if adress:
            adress = f"{adress}%"
            condition += " AND adress like %s"
            params.append(adress)
        if order_status !=-1:
            condition += " AND order_status=%s"
            params.append(order_status)
        if create_date_start:
            condition += " AND create_date>=%s"
            params.append(create_date_start)
        if create_date_end:
            condition += " AND create_date<=%s"
            params.append(create_date_end)
        prize_order_model = PrizeOrderModel(context=self.context)
        if is_cache:
            dependency_key=f"prize_order_list:actid_{act_id}"
            if user_id:
                dependency_key += f"_userid_{user_id}"
            page_list, total = prize_order_model.get_cache_dict_page_list(field, page_index, page_size, condition, "", order_by, params,dependency_key)
        else:
            page_list, total = prize_order_model.get_dict_page_list(field, page_index, page_size, condition, "", order_by, params)
        if is_search_roster == True:
            prize_roster_model = PrizeRosterModel(context=self.context)
            if page_list and len(page_list)>0:
                order_no_list = [str(i['order_no']) for i in page_list]
                order_nos = ",".join(order_no_list)
                prize_roster_list_dict = prize_roster_model.get_dict_list("order_no in (" + order_nos + ")")
                for i in range(len(page_list)):
                    roster_list = [prize_roster for prize_roster in prize_roster_list_dict if page_list[i]["order_no"] == prize_roster["order_no"]]
                    page_list[i]["roster_list"] = roster_list
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def update_prize_order_status(self,app_id,prize_order_id,order_status,express_company="",express_no=""):
        """
        :description: 更新用户奖品订单状态
        :param app_id：应用标识
        :param prize_order_id：奖品订单标识
        :param order_status：订单状态
        :param express_company：快递公司
        :param express_no：快递单号
        :return: 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        now_datetime = SevenHelper.get_now_datetime()
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        prize_order_model = PrizeOrderModel(context=self.context,db_transaction=db_transaction)
        prize_roster_model = PrizeRosterModel(context=self.context,db_transaction=db_transaction)
        invoke_result_data = InvokeResultData()

        prize_order = prize_order_model.get_entity_by_id(prize_order_id)
        if not prize_order:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-1"
            return invoke_result_data
        if prize_order.app_id != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-2"
            return invoke_result_data
        try:
            db_transaction.begin_transaction()
            if order_status == 1:
                if not express_company and not express_no:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message ="快递公司或快递单号不能为空"
                    return invoke_result_data
                update_sql = "order_status=1,express_company=%s,express_no=%s,deliver_date=%s,modify_date=%s"
                params = [express_company, express_no, now_datetime, now_datetime, prize_order_id]
                prize_order_model.update_table(update_sql, "id=%s", params)
                prize_roster_model.update_table("logistics_status=1", "act_id=%s and order_no=%s", [prize_order.act_id,prize_order.order_no])
            if order_status == 2:
                update_sql = "order_status=2,modify_date=%s"
                params = [now_datetime, prize_order_id]
                prize_order_model.update_table(update_sql, "id=%s", params)
                prize_roster_model.update_table("logistics_status=2", "act_id=%s and order_no=%s", [prize_order.act_id,prize_order.order_no])
            else:
                prize_order_model.update_table("order_status=%s,modify_date=%s", "id=%s", [order_status, now_datetime, prize_order_id])
            result = db_transaction.commit_transaction()
            if result == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message ="操作失败"
                return invoke_result_data
                
        except Exception as ex:
            self.context.logging_link_error(traceback.format_exc())
            db_transaction.rollback_transaction()
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="操作失败"
            return invoke_result_data

        return invoke_result_data

    def update_prize_order_seller_remark(self,app_id,prize_order_id,seller_remark):
        """
        :description: 更新用户奖品订单卖家备注
        :param app_id：应用标识
        :param prize_order_id：奖品订单标识
        :param seller_remark：卖家备注
        :return: 实体模型InvokeResultData
        :last_editors: HuangJianYi
        """
        now_datetime = SevenHelper.get_now_datetime()
        prize_order_model = PrizeOrderModel(context=self.context)
        invoke_result_data = InvokeResultData()

        prize_order = prize_order_model.get_entity_by_id(prize_order_id)
        if not prize_order:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-1"
            return invoke_result_data
        if prize_order.app_id!=app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="奖品订单信息不存在-2"
            return invoke_result_data
        prize_order_model.update_table("seller_remark=%s,modify_date=%s", "id=%s", [seller_remark, now_datetime, prize_order_id])
        return invoke_result_data

    def import_prize_order(self,app_id,act_id,content,ref_head_name='小程序订单号'):
        """
        :description: 
        :param app_id：应用标识
        :param act_id：活动标识
        :param content：base64加密后的excel内容
        :param ref_head_name：关联表头名称
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not app_id or not act_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="无效活动,无法导入订单"
            return invoke_result_data

        data = base64.decodebytes(content.encode())
        path = "temp/" + UUIDHelper.get_uuid() + ".xlsx"
        with open(path, 'ba') as f:
            buf = bytearray(data)
            f.write(buf)
        f.close()

        order_no_index = -1
        express_no_index = -1
        express_company_index = -1

        data = ExcelHelper.input(path)
        data_total = len(data)
        # 表格头部
        if data_total > 0:
            title_list = data[0]
            if ref_head_name in title_list:
                order_no_index = title_list.index(ref_head_name)
            if "物流单号" in title_list:
                express_no_index = title_list.index("物流单号")
            if "物流公司" in title_list:
                express_company_index = title_list.index("物流公司")

        if order_no_index == -1 or express_no_index == -1 or express_company_index == -1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="缺少必要字段，无法导入订单"
            return invoke_result_data
        prize_order_model = PrizeOrderModel(context=self.context)
        prize_roster_model = PrizeRosterModel(context=self.context)
        # 数据导入
        for i in range(1, data_total):
            row = data[i]
            order_no = row[order_no_index]
            express_no = row[express_no_index]
            express_company = row[express_company_index]
            if order_no and express_no and express_company:
                now_datetime = SevenHelper.get_now_datetime()
                update_sql = "order_status=1,express_company=%s,express_no=%s,deliver_date=%s,modify_date=%s"
                params = [express_company, express_no, now_datetime, now_datetime, app_id,act_id,order_no]
                prize_order_model.update_table(update_sql, "app_id=%s and act_id=%s and order_no=%s", params)
                prize_roster_model.update_table("logistics_status=1", "app_id=%s and act_id=%s and order_no=%s", [app_id,act_id,order_no])

        os.remove(path)

        return invoke_result_data

    def get_tao_pay_order_list(self,app_id,act_id,user_id,open_id,nick_name,pay_date_start,pay_date_end,page_size=20,page_index=0,field='*'):
        """
        :description: 用户购买订单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户唯一标识
        :param open_id：open_id
        :param nick_name：用户昵称
        :param pay_date_start：订单支付时间开始
        :param pay_date_end：订单支付时间结束
        :param page_size：页大小
        :param page_index：页索引
        :param field：查询字段
        :return: PageInfo
        :last_editors: HuangJianYi
        """
        condition = "app_id=%s and act_id=%s"
        params = [app_id,act_id]
        page_info = PageInfo(page_index, page_size, 0, [])
        
        if not app_id or not act_id:
            return page_info
        if not user_id and not open_id:
            return page_info
        if user_id:
            condition += " AND user_id=%s"
            params.append(user_id)
        if open_id:
            condition += " AND open_id=%s"
            params.append(open_id)
        if nick_name:
            condition += " AND user_nick=%s"
            params.append(nick_name)
        if pay_date_start:
            condition += " AND pay_date>=%s"
            params.append(pay_date_start)
        if pay_date_end:
            condition += " AND pay_date<=%s"
            params.append(pay_date_end)
        page_list, total = TaoPayOrderModel(context=self.context).get_dict_page_list(field, page_index, page_size, condition, "", "pay_date desc", params)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info
    
    def select_prize_order(self,app_id,act_id,user_id,login_token,prize_ids,real_name,telephone,province,city,county,street,address):
        """
        :description: 选择奖品进行下单
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param login_token:用户访问令牌
        :param prize_ids:用户奖品id串，逗号分隔（为空则将所有未下单的奖品进行下单）
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not app_id or not act_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message ="无效活动,无法创建订单"
            return invoke_result_data
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        prize_ids_list = []
        if prize_ids:
            prize_ids_list = prize_ids.split(',')
            for prize_id in prize_ids_list:
                try:
                    prize_id = int(prize_id)    
                except Exception as ex:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message ="存在无法识别的奖品标识"
                    return invoke_result_data
                    
        #获取用户信息
        user_info_dict = user_info_model.get_dict_by_id("act_id=%s and user_id=%s", params=[act_id, user_id])
        if not user_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户不存在"
            return invoke_result_data
        if user_info_dict["login_token"] != login_token:  
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "已在另一台设备登录,无法操作"
            return invoke_result_data
        if int(user_info_dict["user_state"]) == 1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "账号异常,请联系客服处理"
            return invoke_result_data
        
        acquire_lock_name = f"create_prize_order_queue_{act_id}_{user_id}"
        acquire_lock_status, identifier = SevenHelper.redis_acquire_lock(acquire_lock_name)
        if acquire_lock_status == False:
            invoke_result_data.success = False
            invoke_result_data.error_code = "acquire_lock"
            invoke_result_data.error_message = "请求超时,请稍后再试"
            SevenHelper.redis_release_lock(acquire_lock_name, identifier)
            return invoke_result_data
        #用户奖品列表
        if len(prize_ids_list)>0:
            prize_roster_list = prize_roster_model.get_list("act_id=%s and id in (" + prize_ids + ") and prize_status=0",params=[act_id])
            if len(prize_roster_list) == 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "对不起,所选下单奖品不存在"
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                return invoke_result_data
        else:
            prize_roster_list = prize_roster_model.get_list("act_id=%s and prize_status=0")
       
        prize_order_model = PrizeOrderModel(context=self.context)
        now_date = SevenHelper.get_now_datetime()
        prize_order = PrizeOrder()
        prize_order.app_id = app_id
        prize_order.user_id = user_id
        prize_order.user_nick = user_info_dict["user_nick"]
        prize_order.open_id = user_info_dict["open_id"]
        prize_order.act_id = act_id
        prize_order.real_name = real_name
        prize_order.telephone = telephone
        prize_order.province = province
        prize_order.city = city
        prize_order.county = county
        prize_order.street = street
        prize_order.adress = address
        prize_order.order_status = 0
        prize_order.create_date = now_date
        prize_order.modify_date = now_date
        prize_order.order_no = SevenHelper.create_order_id()

        for prize_roster in prize_roster_list:
            prize_roster.order_no = prize_order.order_no
            prize_roster.prize_status = 1
        try:
            db_transaction.begin_transaction()
            prize_order_model.add_entity(prize_order)
            prize_roster_model.update_list(prize_roster_list, "order_no,prize_status")
            result = db_transaction.commit_transaction()
            if result == False:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "对不起,下单失败"
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
                return invoke_result_data
        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("create_prize_order:" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起,下单失败"
            SevenHelper.redis_release_lock(acquire_lock_name, identifier)
            return invoke_result_data

        SevenHelper.redis_release_lock(acquire_lock_name, identifier)
        self._delete_prize_order_dependency_key(act_id)
        invoke_result_data.data = prize_order.__dict__
        return invoke_result_data

    