# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-07-22 11:10:20
@LastEditTime: 2021-08-18 20:12:15
@LastEditors: HuangJianYi
@Description: 
"""

from seven_cloudapp_frame.libs.customize.seven_helper import *
from seven_cloudapp_frame.models.top_base_model import *
from seven_cloudapp_frame.models.db_models.user.user_account_model import *
from seven_cloudapp_frame.models.db_models.user.user_info_model import *
from seven_cloudapp_frame.models.db_models.user.user_black_model import *
from seven_cloudapp_frame.models.db_models.prize.prize_roster_model import *


class UserBaseModel():
    """
    :description: 用户信息基类
    """
    def __init__(self, context):
        self.context = context

    def _get_user_info_id(self, act_id, user_id):
        """
        :description: 生成用户信息唯一标识
        :param act_id：活动标识
        :param user_id：用户标识
        :return: 用户信息唯一标识
        :last_editors: HuangJianYi
        """
        if not act_id or not user_id:
            return 0
        return CryptoHelper.md5_encrypt_int(f"{act_id}_{user_id}")

    def get_user_info_dependency_key(self, act_id, id, open_id=""):
        """
        :description: 获取用户信息缓存key
        :param user_info_id：用户信息标识
        :param open_id：open_id
        :return: 
        :last_editors: HuangJianYi
        """
        if id:
            return  f"user_info:actid_{act_id}_id_{id}"
        else:
            return  f"user_info:actid_{act_id}_openid_{open_id}"

    def _delete_user_info_cache(self,act_id,id):
        """
        :description: 删除用户信息缓存
        :param act_id：活动标识
        :param id：用户信息标识
        :return: 
        :last_editors: HuangJianYi
        """
        cache_key = self.get_user_info_dependency_key(act_id,id)
        redis_init = SevenHelper.redis_init()
        redis_init.delete(cache_key)

    def get_user_info_dict(self,app_id, act_id, user_id,open_id="",is_cache=True):
        """
        :description: 获取用户信息单条记录
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param is_cache：是否缓存
        :return: 返回用户信息
        :last_editors: HuangJianYi
        """
        user_info_dict = None
        if not act_id or (not user_id and not open_id):
            return user_info_dict
        user_info_model = UserInfoModel(context=self.context)
        id = self._get_user_info_id(act_id,user_id)
        dependency_key = self.get_user_info_dependency_key(act_id,id,open_id)
        if id:
            if is_cache:
                user_info_dict = user_info_model.get_cache_dict_by_id(id,dependency_key=dependency_key)
            else:
                user_info_dict = user_info_model.get_dict_by_id(id)
        else:
            if is_cache:
                user_info_dict = user_info_model.get_cache_dict(dependency_key=dependency_key,where="act_id=%s and open_id=%s", params=[act_id, open_id])
            else:
                user_info_dict = user_info_model.get_dict("act_id=%s and open_id=%s", params=[act_id, open_id])
                
        if user_info_dict and user_info_dict["app_id"] != app_id:
            user_info_dict = None
        return user_info_dict
          
    def get_user_list(self, app_id, act_id, page_size=20, page_index=0, user_state=-1, user_id=0, start_date="", end_date="", user_nick="", open_id="", order_by="id desc"):
        """
        :description: 获取用户信息列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_size：条数
        :param page_index：页数
        :param user_state：用户状态
        :param user_id：用户标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param user_nick：昵称
        :param open_id：open_id
        :param order_by：排序
        :return: 返回PageInfo
        :last_editors: HuangJianYi
        """
        page_info = PageInfo(page_index, page_size, 0, [])
        if not act_id:
            return page_info

        condition = "act_id=%s"
        params = [act_id]

        if app_id:
            condition += " AND app_id=%s"
            params.append(app_id)
        if user_id != 0:
            condition += " AND user_id=%s"
            params.append(user_id)
        if user_state != -1:
            condition += " AND user_state=%s"
            params.append(user_state)
        if open_id:
            condition += " AND open_id=%s"
            params.append(open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = UserInfoModel(context=self.context).get_dict_page_list("*", page_index, page_size, condition, order_by=order_by, params=params)

        page_info = PageInfo(page_index, page_size, total, page_list)
    
    def get_join_member_url(self,access_token,app_key,app_secret,is_log):
        """
        :description: 获取加入会员地址
        :param access_token:access_token
        :param app_key:app_key
        :param app_secret:app_secret
        :param is_log:是否记录top请求日志
        :return 
        :last_editors: HuangJianYi
        """
        top_base_model = TopBaseModel(context=self.context)
        return top_base_model.get_join_member_url(access_token,app_key,app_secret,is_log)
    
    def save_user_by_openid(self, app_id, act_id, open_id, user_nick, avatar, union_id=""):
        """
        :description: 获取或更新用户信息（主要用于登录）
        :param app_id：应用标识
        :param act_id：活动标识
        :param open_id：open_id
        :param user_nick：昵称
        :param avatar：头像
        :param union_id：union_id
        :return: 返回用户信息
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not act_id or not open_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data

        acquire_lock_name = f"get_or_add_user_by_openid:{app_id}_{open_id}"
        acquire_lock_status, identifier = SevenHelper.redis_acquire_lock(acquire_lock_name)
        if acquire_lock_status == False:
            invoke_result_data.success = False
            invoke_result_data.error_code = "acquire_lock"
            invoke_result_data.error_message = "请求超时,请稍后再试"
            return invoke_result_data

        user_account_model = UserAccountModel(context=self.context)
        user_info = None
        user_info_model = UserInfoModel(context=self.context)
        now_datetime = SevenHelper.get_now_datetime()
        try:
            user_account = user_account_model.get_entity("open_id=%s",params=[open_id])
            if not user_account:
                user_account = UserAccount()
                user_account.union_id = union_id
                user_account.open_id = open_id
                user_account.user_nick = user_nick
                user_account.avatar = avatar
                user_account.is_auth = 0
                user_account.user_state = 0
                user_account.create_date = now_datetime
                user_account.modify_date = now_datetime
                user_account.id = user_account_model.add_entity(user_account)
            else:
                if user_account.user_nick != user_nick or user_account.avatar != avatar:
                    user_account.user_nick = user_nick
                    user_account.avatar = avatar
                    user_account_model.update_entity(user_account, "user_nick,avatar")
                
            user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
            if not user_info:
                user_info = UserInfo()
                user_info.id = self._get_user_info_id(act_id, user_account.id)
                user_info.app_id = app_id
                user_info.act_id = act_id
                user_info.open_id = open_id
                user_info.user_id = user_account.id
                user_info.is_new = 1
                user_info.user_nick = user_account.user_nick
                user_info.avatar = user_account.avatar
                user_info.user_nick = user_nick if user_nick else user_info.user_nick
                user_info.avatar = avatar if avatar else user_info.avatar
                user_info.create_date = now_datetime
                user_info.modify_date = now_datetime
                user_info.login_token = SevenHelper.get_random(16, 1)
                user_info_model.add_entity(user_info)
            else:
                if user_info.app_id != app_id:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "非法操作"
                    return invoke_result_data
                user_info.user_nick = user_account.user_nick
                user_info.avatar = user_account.avatar
                user_info.is_new = 0
                user_info.modify_date = now_datetime
                user_info.login_token = SevenHelper.get_random(16, 1)
                user_info_model.update_entity(user_info, "modify_date,login_token,is_new,user_nick,avatar")
                
                self._delete_user_info_cache(user_info.act_id,user_info.id)
                    
        except Exception as ex:
            self.context.logging_link_error("【获取或更新用户信息】" + str(ex))
        finally:
                SevenHelper.redis_release_lock(acquire_lock_name, identifier)
        
        invoke_result_data.data = user_info.__dict__
        return invoke_result_data

    def update_user_info(self, app_id, act_id, user_id, open_id, user_nick, avatar,is_member_before=-1,is_favor_before=-1):
        """
        :description: 更新用户信息（主要用于授权更新昵称和头像）
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param open_id：open_id
        :param user_nick：昵称
        :param avatar：头像
        :param is_member_before：初始会员状态
        :param is_favor_before：初始关注状态
        :return: 返回用户信息
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()

        if not act_id or (not user_id and not open_id) or (user_nick == "" and avatar == ""):
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data

        user_account_model = UserAccountModel(context=self.context)
        user_info_dict = None
        user_info_model = UserInfoModel(context=self.context)

        try:
            user_info_dict = self.get_user_info_dict(app_id, act_id, user_id,open_id)
            if not user_info_dict:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "更新失败，找不到用户信息"
                return invoke_result_data
            else:
                if user_info_dict["app_id"] != app_id:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "非法操作"
                    return invoke_result_data
                user_info_dict["is_member_before"] = is_member_before if is_member_before!=-1 else user_info_dict["is_member_before"]
                user_info_dict["is_favor_before"] = is_favor_before if is_favor_before!=-1 else user_info_dict["is_favor_before"]    
                user_info_dict["user_nick"] = user_nick if user_nick else user_info_dict["user_nick"]
                user_info_dict["avatar"] = avatar if avatar else user_info_dict["avatar"]
                user_info_dict["modify_date"] = SevenHelper.get_now_datetime()
                user_info_model.update_table("user_nick=%s,avatar=%s,modify_date=%s,is_member_before=%s,is_favor_before=%s","id=%s",params=[user_info_dict["user_nick"],user_info_dict["avatar"],user_info_dict["modify_date"],user_info_dict["is_member_before"],user_info_dict["is_favor_before"],user_info_dict["id"]])
                
                self._delete_user_info_cache(user_info_dict["act_id"],user_info_dict["id"])
                
                update_sql = ""
                params = []
                if user_nick:
                    update_sql = "user_nick=%s"
                    params.append(user_nick)
                if avatar:
                    update_sql += "," if update_sql else ""
                    update_sql += "avatar=%s"
                    params.append(avatar)
                params.append(user_info_dict["user_id"])
                user_account_model.update_table(update_sql, "id=%s", params=params)

        except Exception as ex:
            self.context.logging_link_error("【更新用户信息】" + str(ex))

        return invoke_result_data

    def update_user_state(self, app_id, act_id, user_id, user_state):
        """
        :description: 更新用户状态
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param user_state: 用户状态（0-正常，1-黑名单）
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        id = self._get_user_info_id(act_id, user_id)
        user_info_model = UserInfoModel(context=self.context)
        user_info = user_info_model.get_entity_by_id(id)
        if not user_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户信息不存在"
            return invoke_result_data
        if user_info.app_id != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "非法操作"
            return invoke_result_data
        if user_info.user_state == user_state:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户状态没变无需更新"
            return invoke_result_data
        modify_date = SevenHelper.get_now_datetime()
        if user_state == 0:
            user_info.relieve_date = modify_date
        user_info.user_state = user_state
        user_info.modify_date = modify_date
        user_info_model.update_entity(user_info, "user_state,relieve_date,modify_date")
        
        self._delete_user_info_cache(user_info.act_id,user_info.id)

        return invoke_result_data

    def update_user_state_by_black(self,app_id,act_id,user_id):
        """
        :description: 用户拉入黑名单
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()

        id = self._get_user_info_id(act_id, user_id)
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_model = UserInfoModel(db_transaction=db_transaction,context=self.context)
        user_black_model = UserBlackModel(db_transaction=db_transaction, context=self.context)

        user_info = user_info_model.get_entity_by_id(id)
        if not user_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户信息不存在"
            return invoke_result_data
        if user_info.app_id != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "非法操作"
            return invoke_result_data
        if user_info.user_state == 1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "该用户已是黑名单"
            return invoke_result_data
        modify_date = SevenHelper.get_now_datetime()
        user_info.user_state = 1
        user_info.modify_date = modify_date

        user_black = user_black_model.get_entity("act_id=%s and user_id=%s", params=[user_info.act_id, user_info.user_id])

        try:
            db_transaction.begin_transaction()

            user_info_model.update_entity(user_info, "user_state,modify_date")
            if not user_black:
                #添加到用户黑名单管理表
                user_black = UserBlack()
                user_black.app_id = user_info.app_id
                user_black.act_id = user_info.act_id
                user_black.open_id = user_info.open_id
                user_black.user_nick = user_info.user_nick
                user_black.black_type = 2
                user_black.refund_order_data = []
                user_black.create_date = self.get_now_datetime()
                user_black_model.add_entity(user_black)
            else:
                user_black.audit_status = 0
                user_black.black_type = 2
                user_black.create_date = self.get_now_datetime()
                user_black_model.update_entity(user_black)

            result = db_transaction.commit_transaction()
            if not result:
                invoke_result_data.success = False
                invoke_result_data.error_code = "fail"
                invoke_result_data.error_message = "系统繁忙,请稍后再试"
                return invoke_result_data
            
            self._delete_user_info_cache(user_info.act_id,user_info.id)

        except Exception as ex:
            db_transaction.rollback_transaction()
            self.context.logging_link_error("【更新用户状态黑名单】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "exception"
            invoke_result_data.error_message = "系统繁忙,请稍后再试"

        return invoke_result_data

    def apply_black_unbind(self,app_id,act_id,user_id, open_id="",reason="误封号,申请解封"):
        """
        :description: 申请黑名单解绑
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param open_id：open_id
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if not act_id or (not user_id and not open_id):
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data
        user_info_dict = self.get_user_info_dict(act_id,user_id,open_id)
        if not user_info_dict:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户信息不存在"
            return invoke_result_data
        if user_info_dict["app_id"] != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "非法操作"
            return invoke_result_data

        if user_info_dict["user_state"] == 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "账号正常,无需申请解封"
            return invoke_result_data
        user_black_model = UserBlackModel(context=self.context)
        user_black = user_black_model.get_entity("act_id=%s and user_id=%s", order_by="create_date desc", params=[act_id, user_id])
        if not user_black:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "账号正常,无需申请解封"
            return invoke_result_data
        if user_black.audit_status == 1:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "请耐心等待客服处理"
            return invoke_result_data

        user_black.audit_status = 1
        user_black.reason = reason
        user_black_model.update_entity(user_black, "audit_status,reason")
        return invoke_result_data
    
    def audit_user_black(self,app_id,black_id,audit_status):
        """
        :description: 审核黑名单
        :param app_id：应用标识
        :param black_id：用户黑名单管理id
        :param audit_status：审核状态(0黑名单1申请中2同意3拒绝)
        :return:
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if black_id <= 0:
            invoke_result_data.success = False
            invoke_result_data.error_code = "param_error"
            invoke_result_data.error_message = "参数不能为空或等于0"
            return invoke_result_data
        user_black_model = UserBlackModel(context=self.context)
        black_info = user_black_model.get_entity_by_id(black_id)
        if not black_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "找不到该条记录"
            return invoke_result_data
        if black_info.app_id != app_id:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "非法操作"
            return invoke_result_data
            
        user_info_model = UserInfoModel(context=self.context)
        id = self._get_user_info_id(black_info.act_id, black_info.user_id)
        user_info = user_info_model.get_entity_by_id(id)
        if not user_info:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "用户信息不存在"
            return invoke_result_data
        audit_date = SevenHelper.get_now_datetime()
        if audit_status == 0:
            user_black_model.update_table("audit_status=%s,audit_date=%s,black_type=2", "id=%s", [audit_status, audit_date, black_id])
            user_info.user_state = 1
            user_info.modify_date = audit_date
            user_info_model.update_entity(user_info,"user_state,modify_date")
        elif audit_status == 2:
            user_black_model.update_table("audit_status=%s,audit_date=%s", "id=%s", [audit_status, audit_date, black_id])
            user_info.user_state = 0
            user_info.modify_date = audit_date
            user_info.relieve_date = audit_date
            user_info_model.update_entity(user_info, "user_state,modify_date,modify_date")
        elif audit_status == 3:
            user_black_model.update_table("audit_status=%s,audit_date=%s", "id=%s", [audit_status, audit_date, black_id])

        self._delete_user_info_cache(user_info.act_id,user_info.id)
        
        return invoke_result_data
        
    def get_black_info_dict(self, app_id, act_id, user_id,is_cache=True):
        """
        :description: 获取黑名单单条记录
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param is_cache：是否缓存
        :return:
        :last_editors: HuangJianYi
        """
        user_black_dict = None
        if not act_id or not user_id:
            return user_black_dict
        user_info_dict = self.get_user_info_dict(app_id, act_id, user_id)
        if not user_info_dict:
            return user_black_dict
        where = "act_id=%s and user_id=%s"
        params = [act_id, user_id]
        user_black_model = UserBlackModel(context=self.context)
        if is_cache:
            user_black_dict = user_black_model.get_cache_dict(dependency_key=f"user_black:{act_id}_{user_id}",where=where, params=params)
        else:
            user_black_dict = user_black_model.get_dict(where, params=params)
        return user_black_dict       

    def get_black_list(self, app_id, act_id, page_size=20, page_index=0, audit_status=-1, user_id=0, start_date="", end_date="", user_nick="", open_id="", order_by="id desc"):
        """
        :description: 获取用户黑名单列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_size：条数
        :param page_index：页数
        :param audit_status：审核状态(0黑名单1申请中2同意3拒绝)
        :param user_id：用户标识
        :param start_date：开始时间
        :param end_date：结束时间
        :param user_nick：昵称
        :param open_id：open_id
        :param order_by：排序
        :return: 返回PageInfo
        :last_editors: HuangJianYi
        """
        page_info = PageInfo(page_index, page_size, 0, [])
        if not act_id:
            return page_info

        condition = "act_id=%s"
        params = [act_id]

        if app_id:
            condition += " AND app_id=%s"
            params.append(app_id)
        if user_id != 0:
            condition += " AND user_id=%s"
            params.append(user_id)
        if audit_status != -1:
            condition += " AND audit_status=%s"
            params.append(audit_status)
        if open_id:
            condition += " AND open_id=%s"
            params.append(open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = UserBlackModel(context=self.context).get_dict_page_list("*", page_index, page_size, condition, order_by=order_by, params=params)
        for user_black in page_list:
            user_black["refund_order_data"] = self.json_loads(user_black["refund_order_data"]) if user_black["refund_order_data"] else []

        page_info = PageInfo(page_index, page_size, total, page_list)

    def get_prize_roster_list(self,app_id,act_id,user_id,open_id='',order_no='',goods_type=-1,prize_type=-1,logistics_status=-1,prize_status=-1,pay_status=-1,page_size=20,page_index=0,order_by="id desc",field="*",is_cache=True):
        """
        :description: 用户中奖记录列表
        :description: 如果有进行数据缓存，创建中奖记录时需清掉依赖建
        :param app_id：应用标识
        :param act_id：活动标识
        :param user_id：用户标识
        :param open_id：open_id
        :param order_no：订单号
        :param goods_type：物品类型（1虚拟2实物）
        :param prize_type：奖品类型(1现货2优惠券3红包4参与奖5预售)
        :param logistics_status：物流状态（0未发货1已发货2不予发货）
        :param prize_status：奖品状态（0未下单（未领取）1已下单（已领取）2已回购10已隐藏（删除）11无需发货）
        :param pay_status：支付状态(0未支付1已支付2已退款3处理中)
        :param page_size：页大小
        :param page_index：页索引
        :param order_by：排序
        :param field：查询字段
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
        if goods_type !=-1:
            condition += " AND goods_type=%s"
            params.append(goods_type)
        if prize_type !=-1:
            condition += " AND prize_type=%s"
            params.append(prize_type)
        if logistics_status !=-1:
            condition += " AND logistics_status=%s"
            params.append(logistics_status)
        if prize_status !=-1:
            condition += " AND prize_status=%s"
            params.append(prize_status)
        if pay_status !=-1:
            condition += " AND pay_status=%s"
            params.append(pay_status)
        
        prize_roster_model = PrizeRosterModel(context=self.context)
        if is_cache:
            dependency_key = f"prize_roster_list:actid_{act_id}"
            if user_id:
                    dependency_key += f"_userid_{user_id}"
            page_list, total = prize_roster_model.get_cache_dict_page_list(field, page_index, page_size, condition, "", order_by, params,dependency_key)
        else:
            page_list, total = prize_roster_model.get_dict_page_list(field, page_index, page_size, condition, "", order_by, params)
        page_info = PageInfo(page_index, page_size, total, page_list)
        return page_info

    def check_pull_black(self,user_info_dict,is_black,refund_count,all_order_data):
        """
        :description: 校验是否拉黑
        :param user_info_dict：用户信息字典
        :param is_black：是否拉黑
        :param refund_count：退款次数
        :param all_order_data:淘宝订单列表
        :return: 
        :last_editors: HuangJianYi
        """
        result = False
        try:
            if user_info_dict["user_state"] == 0 and is_black == 1 and refund_count > 0:
                #退款的订单  子订单存在退款 记录一次
                refund_order_data = [i for i in all_order_data if i["refund_status"] not in self.refund_status()]
                #如果不是黑用户 并且存在退款时间 代表黑用户解禁
                if user_info_dict["relieve_date"] != '1900-01-01 00:00:00':
                    refund_order_data = [i for i in refund_order_data if TimeHelper.format_time_to_datetime(i['pay_time']) > TimeHelper.format_time_to_datetime(user_info_dict["relieve_date"])]
                #超过变成黑用户
                if len(refund_order_data) >= refund_count:
                    result = True
                    user_info_model = UserInfoModel(context=self.context)
                    user_info_model.update_table("user_state=1", "id=%s", user_info_dict["id"])
                    user_black_model = UserBlackModel(context=self.context)
                    user_black = user_black_model.get_entity("act_id=%s and user_id=%s", params=[user_info_dict["act_id"], user_info_dict["user_id"]])
                    if user_black:
                        user_black.black_type = 1
                        user_black.reason = ""
                        user_black.audit_status = 0
                        user_black.audit_remark = ""
                        user_black.refund_count += len(refund_order_data)
                        all_refund_order_data = SevenHelper.json_loads(user_black.refund_order_data)
                        if len(refund_order_data) > 0:
                            for item in refund_order_data:
                                all_refund_order_data.append(item)
                        user_black.refund_order_data = SevenHelper.json_dumps(all_refund_order_data)
                        user_black_model.update_entity(user_black)
                    else:
                        user_black = UserBlack()
                        user_black.app_id = user_info_dict["app_id"]
                        user_black.act_id = user_info_dict["act_id"]
                        user_black.open_id = user_info_dict["open_id"]
                        user_black.user_nick = user_info_dict["user_nick"]
                        user_black.black_type = 1
                        user_black.reason = ""
                        user_black.audit_status = 0
                        user_black.audit_remark = ""
                        user_black.refund_count = len(refund_order_data)
                        user_black.refund_order_data = SevenHelper.json_dumps(refund_order_data)
                        user_black.create_date = SevenHelper.get_now_datetime()
                        user_black_model.add_entity(user_black)
                    self._delete_user_info_cache(user_info_dict["act_id"],user_info_dict["id"])
        except Exception as ex:
            self.context.logging_link_error("【校验是否拉黑】" + str(ex))
            result = False
        return result
 