# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2021-07-15 11:54:54
@LastEditTime: 2021-08-13 18:10:40
@LastEditors: HuangJianYi
:description: 常用帮助类
"""
from seven_framework import *
from seven_framework.redis import *
from emoji import unicode_codes
import random
import datetime
import re
import ast

class SevenHelper:
    """
    :description: 常用帮助类
    """
    @classmethod
    def redis_init(self, db=None, decode_responses=True):
        """
        :description: redis初始化
        :return: redis_cli
        :last_editors: HuangJianYi
        """
        host = config.get_value("redis")["host"]
        port = config.get_value("redis")["port"]
        if not db:
            db = config.get_value("redis")["db"]
        password = config.get_value("redis")["password"]
        redis_cli = RedisHelper.redis_init(host, port, db, password, decode_responses=decode_responses)
        return redis_cli

    @classmethod
    def is_continue_request(self, cache_key, expire=500):
        """
        :description: 请求太频繁校验
        :param cache_key：自定义cache_key
        :param expire：过期时间，单位毫秒
        :return: bool true-代表连续请求进行限制，false-代表跳过限制
        :last_editors: HuangJianYi
        """
        redis_init = self.redis_init()
        post_value = redis_init.get(cache_key)
        if post_value == None:
            redis_init.set(cache_key, 10, px=expire)
            return False
        return True

    @classmethod
    def redis_check_llen(self,queue_name,queue_lenth=100):
        """
         :description: 校验队列长度
         :param queue_name：自定义队列名称
         :param queue_lenth：队列长度
         :return: bool False-代表达到长度限制，进行拦截
         :last_editors: HuangJianYi
         """
        redis_init = SevenHelper.redis_init()
        list_len = redis_init.llen(queue_name)
        if int(list_len) >= int(queue_lenth):
            return False
        else:
            return True

    @classmethod
    def redis_lpush(self, queue_name, value, expire):
        """
         :description: 入队列
         :param queue_name：自定义队列名称
         :param value：加入队列的数据
         :param expire：过期时间，单位秒
         :return: bool true-代表入队成功，false-代表达到长度限制，进行拦截
         :last_editors: HuangJianYi
         """
        redis_init = SevenHelper.redis_init()
        redis_init.lpush(queue_name, json.dumps(value))
        redis_init.expire(queue_name,expire)

    @classmethod
    def redis_lpop(self, queue_name):
        """
         :description: 出队列
         :param queue_name：队列名称
         :return: 
         :last_editors: HuangJianYi
         """
        result = SevenHelper.redis_init().lpop(queue_name)
        return result

    @classmethod
    def redis_acquire_lock(self, lock_name, acquire_time=10, time_out=15):
        """
        :description: 获取一个分布式锁
        :param lock_name：锁定名称
        :param acquire_time: 客户端等待获取锁的时间,单位秒
        :param time_out: 锁的超时时间,单位秒
        :return bool
        :last_editors: HuangJianYi
        """
        identifier = str(uuid.uuid4())
        end = time.time() + acquire_time
        lock = "lock:" + lock_name
        redis_init = SevenHelper.redis_init()
        while time.time() < end:
            if redis_init.setnx(lock, identifier):
                # 给锁设置超时时间, 防止进程崩溃导致其他进程无法获取锁
                redis_init.expire(lock, time_out)
                return True,identifier
            if redis_init.ttl(lock) == -1 or redis_init.ttl(lock) == None:
                redis_init.expire(lock, time_out)
            time.sleep(0.001)
        return False,""

    @classmethod
    def redis_release_lock(self, lock_name, identifier):
        """
        :description: 释放一个锁
        :param lock_name：锁定名称
        :param identifier: identifier
        :return bool
        :last_editors: HuangJianYi
        """
        lock = "lock:" + lock_name
        redis_init = SevenHelper.redis_init()
        pip = redis_init.pipeline(True)
        while True:
            try:
                pip.watch(lock)
                lock_value = redis_init.get(lock)
                if not lock_value:
                    return True
                if lock_value == identifier:
                    pip.multi()
                    pip.delete(lock)
                    pip.execute()
                    return True
                pip.unwatch()
                break
            except Exception:
                pass
        return False

    @classmethod
    def merge_dict_list(self, source_dict_list, source_key, merge_dict_list, merge_key, merge_columns_names=''):
        """
        :description: 两个字典列表合并
        :param source_dict_list：源字典表
        :param source_key：源表用来关联的字段
        :param merge_dict_list：需要合并的字典表
        :param merge_key：需要合并的字典表用来关联的字段
        :param merge_columns_names：需要合并的字典表中需要展示的字段
        :return: 
        :last_editors: HuangJianYi
        """
        result = []
        if merge_columns_names:
            list_key = list(merge_columns_names.split(","))
        else:
            list_key = list(merge_dict_list[0].keys()) if len(merge_dict_list)>0 else []

        for source_dict in source_dict_list:
            info_list = [i for i in merge_dict_list if source_dict[source_key] and str(i[merge_key]) == str(source_dict[source_key])]
            if info_list:
                source_dict = dict(source_dict, **dict.fromkeys(list_key))
                for item in list_key:
                    source_dict[item] = info_list[0].get(item)
            else:
                result_key = []
                for item in list_key:
                    if item not in source_dict.keys():
                        result_key.append(item)
                source_dict = dict(source_dict, **dict.fromkeys(result_key))
            result.append(source_dict)
        return result

    @classmethod
    def auto_mapper(self, s_model, map_dict=None):
        '''
        :description: 对象映射（把map_dict值赋值到实体s_model中）
        :param s_model：需要映射的实体对象
        :param map_dict：被映射的实体字典
        :return: obj
        :last_editors: HuangJingCan
        '''
        if map_dict:
            field_list = s_model.get_field_list()
            for filed in field_list:
                if filed in map_dict:
                    setattr(s_model, filed, map_dict[filed])
        return s_model

    @classmethod
    def get_condition_by_str_list(self, field_name, str_list):
        """
        :description: 根据str_list返回查询条件
        :param field_name: 字段名
        :param str_list: 字符串数组
        :return: 
        :last_editors: HuangJianYi
        """
        if not str_list:
            return ""
        list_str = ','.join(["'%s'" % str(item) for item in str_list])
        return f"{field_name} IN({list_str})"

    @classmethod
    def get_condition_by_int_list(self, field_name, int_list=None):
        '''
        :description: 根据int_list返回查询条件
        :param field_name:字段名
        :param int_list:整形数组
        :return: str
        :last_editors: HuangJianYi
        '''
        if not int_list:
            return ""
        list_str = str(int_list).strip('[').strip(']')
        return f"{field_name} IN({list_str})"

    @classmethod
    def is_ip(self, ip_str):
        """
        :description: 判断是否IP地址
        :param ip_str: ip串
        :return:
        :last_editors: HuangJianYi
        """
        p = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
        if p.match(str(ip_str)):
            return True
        return False

    @classmethod
    def get_first_ip(self):
        """
        :description: 获取第一个IP
        :return:
        """
        ip = self.get_remote_ip()
        if ip and "," in ip:
            return ip.split(",")[0]
        else:
            return ip

    @classmethod
    def to_file_size(self, size):
        """
        :description: 文件大小格式化
        :param size：文件大小
        :return: str
        :last_editors: HuangJingCan
        """
        if size < 1000:
            return '%i' % size + 'size'
        elif 1024 <= size < 1048576:
            return '%.2f' % float(size / 1024) + 'KB'
        elif 1048576 <= size < 1073741824:
            return '%.2f' % float(size / 1048576) + 'MB'
        elif 1073741824 <= size < 1000000000000:
            return '%.2f' % float(size / 1073741824) + 'GB'
        elif 1000000000000 <= size:
            return '%.2f' % float(size / 1000000000000) + 'TB'

    @classmethod
    def get_random(self, num, many):
        """
        :description: 获取随机数
        :param num：位数
        :param many：个数
        :return: str
        :last_editors: CaiYouBin
        """
        result = ""
        for x in range(many):
            s = ""
            for i in range(num):
                # n=1 生成数字  n=2 生成字母
                n = random.randint(1, 2)
                if n == 1:
                    numb = random.randint(0, 9)
                    s += str(numb)
                else:
                    nn = random.randint(1, 2)
                    cc = random.randint(1, 26)
                    if nn == 1:
                        numb = chr(64 + cc)
                        s += numb
                    else:
                        numb = chr(96 + cc)
                        s += numb
            result += s
        return result

    @classmethod
    def get_random_switch_string(self, random_str, split_chars=","):
        """
        :description: 随机取得字符串
        :param trimChars：根据什么符号进行分割
        :return: str
        :last_editors: HuangJingCan
        """
        if random_str == "":
            return ""
        random_list = [i for i in random_str.split(split_chars) if i != ""]
        return random.choice(random_list)

    @classmethod
    def get_now_datetime(self):
        """
        :description: 获取当前时间
        :return: str
        :last_editors: HuangJingCan
        """
        add_hours = config.get_value("add_hours", 0)
        return TimeHelper.add_hours_by_format_time(hour=add_hours)

    @classmethod
    def get_now_int(self, hours=0,fmt='%Y%m%d%H%M%S'):
        """
        :description: 获取整形的时间 格式为yyyyMMddHHmmss，如2009年12月27日9点10分10秒表示为20091227091010
        :param hours: 需要增加的小时数
        :param fmt: 时间格式
        :return:
        :last_editors: HuangJianYi
        """
        now_date = (datetime.datetime.now() + datetime.timedelta(hours=hours))
        return int(now_date.strftime(fmt))

    @classmethod
    def get_now_hour_int(self, hours=0):
        """
        :description: 获取整形的小时2020050612
        :param hours: 需要增加的小时数
        :return: int（2020050612）
        :last_editors: HuangJianYi
        """
        return self.get_now_int(fmt='%Y%m%d%H')

    @classmethod
    def get_now_day_int(self, hours=0):
        """
        :description: 获取整形的天20200506
        :param hours: 需要增加的小时数
        :return: int（20200506）
        :last_editors: HuangJianYi
        """
        return self.get_now_int(fmt='%Y%m%d')

    @classmethod
    def get_now_month_int(self, hours=0):
        """
        :description: 获取整形的月202005
        :param hours: 需要增加的小时数
        :return: int（202005）
        :last_editors: HuangJianYi
        """
        return self.get_now_int(fmt='%Y%m')

    @classmethod
    def get_date_list(self, start_date, end_date):
        """
        :description: 两个日期之间的日期列表
        :param start_date：开始日期
        :param end_date：结束日期
        :return: list
        :last_editors: HuangJianYi
        """
        if not start_date or not end_date:
            return []

        datestart = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        dateend = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        date_list = []

        while datestart < dateend:
            date_list.append(datestart.strftime('%Y-%m-%d'))
            datestart += datetime.timedelta(days=1)
        return date_list

    @classmethod
    def get_page_count(self, page_size, record_count):
        """
        @description: 计算页数
        @param page_size：页大小
        @param record_count：总记录数
        @return: 页数
        @last_editors: HuangJianYi
        """
        page_count = record_count / page_size + 1
        if page_size == 0:
            page_count = 0
        if record_count % page_size == 0:
            page_count = record_count / page_size
        page_count = int(page_count)
        return page_count

    @classmethod
    def create_order_id(self, ran=5):
        """
        :description: 生成订单号
        :param ran：随机数位数，默认5位随机数（0-5）
        :return: 25位的订单号
        :last_editors: HuangJianYi
        """
        ran_num = ""
        if ran == 1:
            ran_num = random.randint(0, 9)
        elif ran == 2:
            ran_num = random.randint(10, 99)
        elif ran == 3:
            ran_num = random.randint(100, 999)
        elif ran == 4:
            ran_num = random.randint(1000, 9999)
        elif ran == 5:
            ran_num = random.randint(10000, 99999)
        # cur_time = TimeHelper.get_now_format_time('%Y%m%d%H%M%S%f')
        cur_time = TimeHelper.get_now_timestamp(True)
        order_id = str(cur_time) + str(ran_num)
        return order_id

    @classmethod
    def emoji_base64_to_emoji(self, text_str):
        """
        :description: 把加密后的表情还原
        :param text_str: 加密后的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        results = re.findall('\[em_(.*?)\]', text_str)
        if results:
            for item in results:
                text_str = text_str.replace("[em_{0}]".format(item), self.base64_encode(item))
        return text_str

    @classmethod
    def emoji_to_emoji_base64(self, text_str):
        """
        :description: emoji表情转为[em_xxx]形式存于数据库,打包每一个emoji
        :description: 性能遇到问题时重新设计转换程序
        :param text_str: 未加密的字符串
        :return: 解密后的表情字符串
        :last_editors: HuangJianYi 
        """
        list_e = []
        for i in text_str:
            list_e.append(i)
        for location, item_emoji in enumerate(text_str):
            if item_emoji in unicode_codes.UNICODE_EMOJI:
                bytes_item_emoji = item_emoji.encode("utf-8")
                emoji_base64 = self.base64_decode(bytes_item_emoji)
                list_e[location] = "[em_" + emoji_base64 + "]"

        return "".join(list_e)

    @classmethod
    def json_dumps(self, rep_dic):
        """
        :description: 将字典转化为字符串
        :param rep_dic：字典对象
        :return: str
        :last_editors: HuangJianYi
        """
        if isinstance(rep_dic, str):
            rep_dic = ast.literal_eval(rep_dic)
        if hasattr(rep_dic, '__dict__'):
            rep_dic = rep_dic.__dict__
        return json.dumps(rep_dic, ensure_ascii=False, cls=JsonEncoder, default=lambda x: (x.__dict__ if not isinstance(x, datetime.datetime) else datetime.datetime.strftime(x, '%Y-%m-%d %H:%M:%S')) if not isinstance(x, decimal.Decimal) else float(x), sort_keys=False, indent=1)

    @classmethod
    def json_loads(self, rep_str):
        """
        :description: 将字符串转化为字典
        :param rep_str：str
        :return: dict
        :last_editors: HuangJianYi
        """
        try:
            return json.loads(rep_str)
        except Exception as ex:
            return json.loads(self.json_dumps(rep_str))
