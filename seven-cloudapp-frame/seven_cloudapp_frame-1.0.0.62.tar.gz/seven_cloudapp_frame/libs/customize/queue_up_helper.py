# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-23 11:18:54
@LastEditTime: 2021-08-24 18:27:53
@LastEditors: HuangJianYi
@Description: 排队系统帮助类
"""
from seven_framework import *
from seven_cloudapp_frame.models.seven_model import *
from seven_cloudapp_frame.libs.customize.seven_helper import *


class QueueUpHelper:
    """
    :description: 排队系统帮助类 提供加入排队、退出排队、单个查询排队情况、批量查询排队情况、更新可操作时间、签到、清空队列等功能
    """
    logger_error = Logger.get_logger_by_name("log_error")

    @classmethod
    def _get_zset_name(self, queue_name):
        """
        :description: 获取排行集合名称，集合用于排行榜，排第一的优先操作
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = "queueup_zset"
        if queue_name:
            zset_name += ":" + str(queue_name)
        return zset_name

    @classmethod
    def _get_zset_time_name(self, queue_name):
        """
        :description: 获取时间集合名称，集合用于设定用户的过期倒计时时间，然后踢出队列，防止长期占用位置
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        zset_name = "queueup_zset_time"
        if queue_name:
            zset_name += ":" + str(queue_name)
        return zset_name

    @classmethod
    def _get_count_name(self, queue_name):
        """
        :description: 获取排队号计数名称
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        count_name = "queueup_count"
        if queue_name:
            count_name += ":" + str(SevenHelper.get_now_day_int()) + "_" + str(queue_name)
        return count_name

    @classmethod
    def _get_user_hash_name(self):
        """
        :description: 获取用户关联队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        return "queueup_user_list"

    @classmethod
    def _get_queue_no(self, queue_name):
        """
        :description: 获取排队号
        :param queue_name：队列名称
        :return: 
        :last_editors: HuangJianYi
        """
        count_name = self._get_count_name(queue_name)
        redis_init = SevenHelper.redis_init()
        queue_no = redis_init.incr(count_name, 1)
        redis_init.expire(count_name, 24 * 3600)
        return queue_no

    @classmethod
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

    @classmethod
    def _delete_expire_user(self, queue_name, expire_time):
        """
        :description: 删除未操作的用户排队信息
        :param queue_name：队列名称
        :param expire_time：过期时间,单位秒,为0不进行删除操作
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        if SevenHelper.is_continue_request(f"delete_expire_user:{queue_name}", 500) == True:
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "对不起,请500毫秒后再试"
            return invoke_result_data
        try:
            if expire_time <= 0:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "不进行删除操作"
                return invoke_result_data
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            zset_time_name = self._get_zset_time_name(queue_name)
            end_time = TimeHelper.get_now_timestamp() - int(expire_time)
            value_list = redis_init.zrangebyscore(zset_time_name, 0, end_time)
            if len(value_list) > 0:
                del_hash_key_list = []
                for user_id in value_list:
                    del_hash_key_list.append(f"userid_{user_id}_queuename_{queue_name}")
                if len(del_hash_key_list) > 0:
                    del_hash_key_list = tuple(del_hash_key_list)
                    redis_init.hdel(self._get_user_hash_name(), *del_hash_key_list)
                value_list = tuple(value_list)
                redis_init.zrem(zset_time_name, *value_list)
                redis_init.zrem(zset_name, *value_list)

            invoke_result_data.data = len(value_list)
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【删除未操作的排队信息】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "删除未操作的排队信息失败"
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
            zset_time_name = self._get_zset_time_name(queue_name)
            hash_name = self._get_user_hash_name()
            zset_result = redis_init.delete(zset_name)
            zset_time_result = redis_init.delete(zset_time_name)
            hash_result = 1
            match_result = redis_init.hscan_iter(hash_name, match=f'*_queuename_{queue_name}')
            queue_name_list = []
            for item in match_result:
                queue_name_list.append(item[0])
            if len(queue_name_list) > 0:
                hash_del_keys = tuple(queue_name_list)
                hash_result = redis_init.hdel(hash_name, *hash_del_keys)

            if zset_result > 0 and zset_time_result > 0 and hash_result > 0:
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

    @classmethod
    def queue(self, queue_name, user_id, user_nick="", queue_length=100):
        """
        :description: 加入排队
        :param act_id：活动标识
        :param queue_name：队列名称
        :param user_id 用户标识
        :param user_nick 用户昵称
        :param queue_length：队列的长度
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            zset_name = self._get_zset_name(queue_name)
            zset_time_name = self._get_zset_time_name(queue_name)
            data = str(user_id)
            redis_init = SevenHelper.redis_init()
            if self._get_queue_num(queue_name) >= queue_length:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "当前排队人数过多,请稍后再来"
                return invoke_result_data
            else:
                if not redis_init.zscore(zset_name, data):
                    score = TimeHelper.get_now_timestamp()
                    queue_no = self._get_queue_no(queue_name)
                    redis_init.zadd(zset_name, {data: queue_no})
                    redis_init.expire(zset_name, 7 * 24 * 3600)

                    redis_init.zadd(zset_time_name, {data: score})
                    redis_init.expire(zset_time_name, 7 * 24 * 3600)

                    query_detail = {}
                    query_detail["queue_name"] = queue_name  #排队名称
                    query_detail["queue_no"] = queue_no  #排队号
                    query_detail["user_id"] = data  #用户标识
                    query_detail["user_nick"] = user_nick  #用户昵称
                    query_detail["queue_date"] = SevenHelper.get_now_datetime()  #入队时间

                    #添加用户所有正在排队的队列到集合中
                    hash_name = self._get_user_hash_name()
                    hash_key = f"userid_{data}_queuename_{queue_name}"
                    redis_init.hsetnx(hash_name, hash_key, SevenHelper.json_dumps(query_detail))
                    redis_init.expire(hash_name, 7 * 24 * 3600)

                    query_user = {}
                    query_user["queue_no"] = query_detail["queue_no"]  #排队号
                    query_user["queue_num"] = self._get_queue_num(queue_name)  #当前排队人数
                    query_user["queue_index"] = int(redis_init.zrank(zset_name, data)) + 1  #当前位置
                    query_user["before_num"] = query_user["queue_index"] - 1  #排在前面的人数
                    invoke_result_data.data = query_user
                    return invoke_result_data
                else:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "该用户已在队列中,请勿重复排队"
                    return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【加入排队】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
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
            zset_time_name = self._get_zset_time_name(queue_name)
            data = str(user_id)
            redis_init = SevenHelper.redis_init()
            if redis_init.zscore(zset_name, data):
                redis_init.zrem(zset_name, data)
                redis_init.zrem(zset_time_name, data)
                redis_init.hdel(self._get_user_hash_name(), f"userid_{data}_queuename_{queue_name}")
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "未查到该用户的排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【退出排队】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "退出排队失败"
            return invoke_result_data

    @classmethod
    def query(self, queue_name, user_id, expire_time=300):
        """
        :description: 查询排队情况
        :param queue_name：队列名称
        :param user_id：用户标识
        :param expire_time：过期时间,单位秒,为0不进行删除操作
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            data = str(user_id)

            #删除未操作的排队信息
            self._delete_expire_user(queue_name, expire_time)

            #判断是否存在排队信息
            score = redis_init.zscore(zset_name, data)
            if score:
                query_user = {}
                query_user["queue_name"] = queue_name  #队列名称
                query_user["queue_no"] = int(score)  #排队号
                query_user["total_num"] = self._get_queue_num(queue_name)  #总排队人数
                query_user["queue_index"] = int(redis_init.zrank(zset_name, data)) + 1  #当前位置
                query_user["before_num"] = query_user["queue_index"] - 1  #排在前面的人数
                hash_value = redis_init.hget(self._get_user_hash_name(), f"userid_{data}_queuename_{queue_name}")
                hash_value = SevenHelper.json_loads(hash_value) if hash_value else {}
                query_user["start_date"] = hash_value["start_date"] if hash_value.__contains__("start_date") else ''
                query_user["end_date"] = hash_value["end_date"] if hash_value.__contains__("end_date") else ''
                query_user["queue_date"] = hash_value["queue_date"] if hash_value.__contains__("queue_date") else ''

                invoke_result_data.data = query_user
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "未查到排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【查询实时排队情况】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data

    @classmethod
    def muti_query(self, user_id, expire_time=300):
        """
        :description: 批量查询排队情况
        :param user_id：用户标识
        :param expire_time：过期时间，单位秒，为0不进行删除操作
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        invoke_result_data.data = []
        try:
            redis_init = SevenHelper.redis_init()
            hash_name = self._get_user_hash_name()
            data = str(user_id)
            match_result = redis_init.hscan_iter(hash_name, match=f'userid_{data}_*')
            for item in match_result:
                hash_value = SevenHelper.json_loads(item[1])
                query_invoke_result_data = self.query(hash_value["queue_name"], user_id, expire_time)
                if query_invoke_result_data.success == True:
                    invoke_result_data.data.append(query_invoke_result_data.data)
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【批量查询实时排队情况】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data

    @classmethod
    def update_time(self, queue_name, user_id, operate_time=0):
        """
        :description: 更新可操作时间，用于操作倒计时，时间到则踢出队列
        :param queue_name：队列名称
        :param user_id：用户标识
        :param operate_time：增加的操作时间，单位秒
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_time_name = self._get_zset_time_name(queue_name)
            data = str(user_id)
            score = redis_init.zscore(zset_time_name, data)
            if score and operate_time > 0:
                redis_init.zincrby(zset_time_name, operate_time, data)
                hash_name = self._get_user_hash_name()
                hash_key = f"userid_{data}_queuename_{queue_name}"
                hash_value = redis_init.hget(hash_name, hash_key)
                if not hash_value:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "更新可操作时间失败"
                    return invoke_result_data
                hash_value = SevenHelper.json_loads(hash_value)
                end_timestamp = int(score) + int(operate_time)
                hash_value["end_date"] = TimeHelper.timestamp_to_format_time(end_timestamp)
                redis_init.hset(hash_name, hash_key, SevenHelper.json_dumps(hash_value))
            return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【更新可操作时间】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "更新可操作时间失败"
            return invoke_result_data

    @classmethod
    def sign(self, queue_name, user_id, quit_other_queue=True, operate_time=300):
        """
        :description: 签到操作（证明排队的人做出应答，开始办理业务，更新开始操作时间并且将当前用户在其他队列中踢掉）
        :param queue_name：队列名称
        :param user_id：用户标识
        :param quit_other_queue：是否退出其他正在排队的队列，True是False否
        :param operate_time：操作时间，单位秒，如果为0则不重置过期时间，默认为排队未操作的过期时间，不为0则是以当前时间作为开始时间并加上可以操作的时间作为结束时间
        :return: 
        :last_editors: HuangJianYi
        """
        invoke_result_data = InvokeResultData()
        try:
            redis_init = SevenHelper.redis_init()
            zset_name = self._get_zset_name(queue_name)
            zset_time_name = self._get_zset_time_name(queue_name)
            data = str(user_id)
            #判断是否存在排队信息
            score = redis_init.zscore(zset_time_name, data)
            if score:
                queue_index = int(redis_init.zrank(zset_name, data)) + 1  #当前位置
                if queue_index != 1:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "前面还有人在排队,请耐心等待"
                    return invoke_result_data
                start_timestamp = TimeHelper.get_now_timestamp()
                end_timestamp = start_timestamp + int(operate_time) if operate_time > 0 else int(score)
                if operate_time > 0:
                    redis_init.zadd(zset_time_name, {data: end_timestamp})
                hash_name = self._get_user_hash_name()
                hash_key = f"userid_{data}_queuename_{queue_name}"
                hash_value = redis_init.hget(hash_name, hash_key)
                if not hash_value:
                    invoke_result_data.success = False
                    invoke_result_data.error_code = "error"
                    invoke_result_data.error_message = "未查到排队情况,请先排队"
                    return invoke_result_data
                hash_value = SevenHelper.json_loads(hash_value)
                hash_value["start_date"] = TimeHelper.timestamp_to_format_time(start_timestamp)
                hash_value["end_date"] = TimeHelper.timestamp_to_format_time(end_timestamp)
                redis_init.hset(hash_name, hash_key, SevenHelper.json_dumps(hash_value))
                if quit_other_queue == True:
                    #踢掉在其他队列中的排队
                    match_result = redis_init.hscan_iter(hash_name, match=f'userid_{data}_*')
                    for item in match_result:
                        hash_value = SevenHelper.json_loads(item[1])
                        if hash_value["queue_name"] == queue_name:
                            continue
                        self.pop(hash_value["queue_name"], data)
                invoke_result_data.data = hash_value
                return invoke_result_data
            else:
                invoke_result_data.success = False
                invoke_result_data.error_code = "error"
                invoke_result_data.error_message = "未查到排队情况,请先排队"
                return invoke_result_data
        except Exception as ex:
            self.logger_error.error("【签到操作】" + str(ex))
            invoke_result_data.success = False
            invoke_result_data.error_code = "error"
            invoke_result_data.error_message = "未查到排队情况,请先排队"
            return invoke_result_data
