# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-23 11:18:54
@LastEditTime: 2021-08-23 13:59:27
@LastEditors: HuangJianYi
@Description: 排队系统
"""
from seven_framework import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *

class QueueHelper:
    """
    :description: 排队系统基类
    """
    logger_error = Logger.get_logger_by_name("log_error")

    def _get_zset_name(self, queue_name):
        """
        :description: 获取有序集合名称
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = "query_zset"
        if queue_name:
            zset_name += ":" + str(queue_name)
        return zset_name

    def _get_list_name(self, queue_name):
        """
        :description: 获取列表名称
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        list_name = "query_list"
        if queue_name:
            list_name += ":" + str(queue_name)
        return list_name

    def _get_count_name(self, queue_name):
        """
        :description: 获取排队计数名称
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        count_name = "query_count"
        if queue_name:
            count_name += ":" + str(queue_name)
        return count_name

    def _get_queue_no(self, queue_name):
        """
        :description: 获取排队号
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        count_name = self._get_count_name(queue_name)
        redis_init = SevenHelper.redis_init()
        queue_no =  redis_init.incr(count_name,1)
        redis_init.expire(count_name, 24*3600)
        return queue_no

    def _get_queue_num(self, queue_name):
        """
        :description: 获取当前排队人数
        :param act_id：活动标识
        :param module_id：活动模块标识
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = self._get_zset_name(queue_name)
        redis_init = SevenHelper.redis_init()
        return redis_init.zcard(zset_name)

    def _delete_expire_user(self, queue_name,expire_time):
        """
        :description: 删除未操作的排队信息
        :param queue_name：队列名称
        :param expire_time：过期时间 单位秒
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            if expire_time <=0:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "不进行删除操作"
                return invoke_result_data
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            list_name = self._get_list_name(queue_name)
            end_time = TimeHelper.get_now_timestamp() - int(expire_time)
            retain_index = redis_init.zremrangebyscore(zset_name, 0, end_time)
            if retain_index > 0:
                redis_init.ltrim(list_name,retain_index,-1)
            invoke_result_data.data = retain_index
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【删除未操作的排队信息】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code ="error"
            invoke_result_data.error_message = "删除未操作的排队信息失败"
            return invoke_result_data

    @classmethod
    def queue(self, queue_name, user_id, user_nick, queue_length=100):
        """
        :description: 加入排队
        :param act_id：活动标识
        :param queue_name：队列名称
        :param user_id 用户标识
        :param user_nick：用户昵称
        :param queue_length：队列的长度
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            zset_name = self._get_zset_name(queue_name)
            data = str(user_id)
            redis_init = SevenHelper.redis_init()
            if self._get_queue_num(queue_name) >= queue_length:
                invoke_result_data.success = False
                invoke_result_data.error_code ="error"
                invoke_result_data.error_message = "当前排队人数过多,请稍后再来"
                return invoke_result_data
            else:
                if not redis_init.zscore(zset_name,data):
                    score = TimeHelper.get_now_timestamp()
                    redis_init.zadd(zset_name, {data: score})
                    redis_init.expire(zset_name,24*3600)

                    query_detail = {}
                    query_detail["queue_no"] = self._get_queue_no(queue_name) #排队号
                    query_detail["user_id"] = data  #用户标识
                    query_detail["user_nick"] = user_nick  #用户昵称
                    query_detail["queue_date"] = SevenHelper.get_now_datetime() #入队时间

                    list_name = self._get_list_name(queue_name)
                    redis_init.rpush(list_name, SevenHelper.json_dumps(query_detail))
                    redis_init.expire(list_name,24*3600)

                    query_user = {}
                    query_user["queue_no"] = query_detail["queue_no"] #排队号
                    query_user["queue_num"] = self._get_queue_num(queue_name) #当前排队人数
                    query_user["queue_index"] = int(redis_init.zrank(zset_name,data)) + 1 #当前位置
                    query_user["before_num"] = query_user["queue_index"] - 1  #排在前面的人数
                    invoke_result_data.data = query_user
                    return invoke_result_data
                else:
                    invoke_result_data.success = False
                    invoke_result_data.error_code ="error"
                    invoke_result_data.error_message = "该用户已在队列中,请勿重复排队"
                    return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【加入排队】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code ="error"
            invoke_result_data.error_message = "排队失败,请稍后再来"
            return invoke_result_data

    @classmethod
    def pop(self, queue_name, user_id):
        """
        :description: 退出排队
        :param queue_name：队列名称
        :param user_id 用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            zset_name = self._get_zset_name(queue_name)
            data = str(user_id)
            redis_init = SevenHelper.redis_init()
            list_name = self._get_list_name(queue_name)
            if redis_init.zscore(zset_name,data):
                cur_index = int(redis_init.zrank(zset_name,data)) #当前位置
                list_value = redis_init.lindex(list_name,cur_index)
                redis_init.zrem(zset_name,data)
                redis_init.lrem(list_name, 0, list_value)
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code ="error"
                invoke_result_data.error_message = "未查到该用户的排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【退出排队】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code ="error"
            invoke_result_data.error_message = "退出排队失败"
            return invoke_result_data

    @classmethod
    def query(self, queue_name, user_id,expire_time=10):
        """
        :description: 查询实时排队情况
        :param queue_name：队列名称
        :param user_id：用户标识
        :param expire_time：过期时间 单位秒
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            list_name = self._get_list_name(queue_name)
            data = str(user_id)

            #删除未操作的排队信息
            self._delete_expire_user(queue_name, expire_time)

            #判断是否存在排队信息
            if redis_init.zscore(zset_name,data):
                cur_index = int(redis_init.zrank(zset_name,data)) #当前位置
                list_value = redis_init.lindex(list_name,cur_index)
                list_value = SevenHelper.json_loads(list_value) if list_value else {}
                query_user = {}
                query_user["queue_no"] = list_value["queue_no"] #排队号
                query_user["total_num"] = self._get_queue_num(queue_name) #总排队人数
                query_user["queue_index"] = int(redis_init.zrank(zset_name,data)) + 1 #当前位置
                query_user["before_num"] = query_user["queue_index"] - 1  #排在前面的人数
                invoke_result_data.data = query_user
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code ="error"
                invoke_result_data.error_message = "未查到排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【查询实时排队情况】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code ="error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data

    @classmethod
    def update_time(self, queue_name, user_id):
        """
        :description: 更新操作时间，用于判断是否长期未操作
        :param queue_name：队列名称
        :param user_id：用户标识
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            data = str(user_id)
            if redis_init.zscore(zset_name,data):
                score = TimeHelper.get_now_timestamp()
                redis_init.zadd(zset_name, {data: score})
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【更新操作时间】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code ="error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data

    @classmethod
    def clear(self, queue_name):
        """
        :description: 清空排队
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            list_name = self._get_list_name(queue_name)

            zset_result = redis_init.delete(zset_name)
            list_result = redis_init.delete(list_name)
            if zset_result and list_result:
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "无排队数据"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【清空排队】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "无排队数据"
            return invoke_result_data