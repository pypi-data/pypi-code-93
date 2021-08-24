"""

"""

import time
import functools
import logging
import sys
import random
import traceback
import json
import gc
import pandas as pd
import numpy as np

# 导入常用的固定路径(多平台通用)
from kw618._file_path import *
from kw618.k_pandas.utils_pandas import *

# AES加密使用
import base64
#注：python3 安装 Crypto 是 pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple pycryptodome<br><br>
from Crypto.Cipher import AES
import hashlib




# 个人用于记录报错内容的log装饰器
def log_error(log_directory=f"{os.getcwd()}/log", throw_error=False):
    """
        params:
            log_directory: 你要存储log的目录路径 (默认是当前路径)

    """
    # 作为装饰器时, 一定要加上(); 否则就不会返回内部的decorate函数了
    # 如果没有传入log的存放目录, 默认使用上述目录
    def decorate(func):
        def record_error(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                module_name = get_this_module_name()
                func_name = func.__name__
                kkprint(module_name=module_name, func_name=func_name)
                tb_txt = traceback.format_exc(limit=5) # limit参数: 表示traceback最多到第几层
                if not os.path.exists(log_directory): # 如果没有这个log的目录路径, 则创建这个文件夹
                    os.mkdir(log_directory)
                log_file_path = f"{log_directory}/{module_name}_error.log"
                with open(log_file_path, "a", encoding="utf-8") as f:
                    print(f"\n【捕获到异常】\n{tb_txt}\n【异常存储路径】: {log_file_path}\n")
                    log_msg = tb_txt
                    this_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    f.write(f"{this_time}\n{log_msg}\n\n\n")
                # 有时候需要把错误内容抛出, 在更外层捕获 (通过'消费者多线程池'来捕获,让其url进入到error_queue)
                if throw_error:
                    raise Exception(tb_txt)
        return record_error
    return decorate

# # 个人用于记录报错内容的log装饰器
# def log_error(log_directory=f"{FILE_PATH_FOR_HOME}/Log/ttt_log", throw_error=False):
#     """
#         params:
#             log_directory: 你要存储log的目录路径 (默认是当前路径)
#
#     """
#     # 作为装饰器时, 一定要加上(); 否则就不会返回内部的decorate函数了
#     # 如果没有传入log的存放目录, 默认使用上述目录
#     def decorate(func):
#         def record_error(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except Exception as e:
#                 module_name = get_this_module_name()
#                 func_name = func.__name__ # 暂时没利用, 可删
#                 kkprint(module_name=module_name, func_name=func_name)
#                 tb_txt = traceback.format_exc(limit=5) # limit参数: 表示traceback最多到第几层
#                 log_file_path = f"{log_directory}/{module_name}_error.log"
#                 with open(log_file_path, "a", encoding="utf-8") as f:
#                     print(f"\n【捕获到异常】\n{tb_txt}\n【异常存储路径】: {log_file_path}\n")
#                     log_msg = tb_txt
#                     this_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#                     f.write(f"{this_time}\n{log_msg}\n\n\n")
#                 # 有时候需要把错误内容抛出, 在更外层捕获 (通过'消费者多线程池'来捕获,让其url进入到error_queue)
#                 if throw_error:
#                     raise Exception(tb_txt)
#         return record_error
#     return decorate
#

def timer(func):
    """装饰器：记录并打印函数耗时"""
    def decorated(*args, **kwargs):
        st = time.time()
        ret = func(*args, **kwargs)
        module_name = get_this_module_name()
        func_name = func.__name__
        # kkprint(module_name=module_name, func_name=func_name)
        print(f'\n[计时器]: \n模块"{module_name}" -- 函数"{func_name}": 执行时长: {time.time() - st} 秒\n')
        return ret
    return decorated


# python官网的例子
def logged(level, name=None, message=None):
    """
    这是python cookbook 中官方写写的log案例
    Add logging to a function. level is the logging
    level, name is the logger name, and message is the
    log message. If name and message aren't specified,
    they default to the function's module and name.

    可以看到, 如果你想要给装饰器传参, 就需要在decorate外面再嵌套一层函数: 总共3层
    """
    def decorate(func): # 此处一定只有一个func形参
        logname = name if name else func.__module__
        log = logging.getLogger(logname)
        logmsg = message if message else func.__name__

        @functools.wraps(func) # 这里的装饰器可以修改__name__的问题(其实没啥用, 反正写上更好就对了, 管他呢)
        def wrapper(*args, **kwargs):  # 此处的形参一定是(*args, **kwargs), 并且与下面return中传入的参数一致!!
            log.log(level, logmsg)
            return func(*args, **kwargs) # 一定要记得return
        return wrapper  # 返回的函数名称一定和上面定义(warpper)的一致!!
    return decorate

# Example use
# @logged(logging.DEBUG)
# def add(x, y):
#     return x + y
#
# @logged(logging.CRITICAL, 'example')
# def spam():
#     print('Spam!')



def get_this_function_name():
    function_name = sys._getframe().f_code.co_name

def get_this_module_name():
    "获取本函数所在脚本的模块名称"
    argv_str = sys.argv[-1]
    return argv_str.split("/")[-1][:-3]


def sprint(**kwargs):
    """
        主要使用场景: 调试bug时候, 经常要打印某个变量名, 是否正确得到, 每次手动写print, 烦的一批!!!
                    遂, 写成了通用接口
        tips:
            与kprint的区别:  sprint只显示一行, 更加简洁   (意为: simply print)
    """
    "kwargs就是一个dict类型"
    for k, v in kwargs.items():
        print(f"\n变量'{k}'--({type(v)})----> {v}\n")

def kprint(**kwargs):
    """
        主要使用场景: 调试bug时候, 经常要打印某个变量名, 是否正确得到, 每次手动写print, 烦的一批!!!
                    遂, 写成了通用接口
    """
    "kwargs就是一个dict类型"
    for k, v in kwargs.items():
        # print(f"\n【变量'{k}'】: {v}, {type(v)}\n\n")

        # int型是没有len()方法的, 所以做了一个判断....(麻烦)
        if hasattr(v, "__len__"): # 是否有__len__魔法方法 (用于测算长度用的)
            print(f"\n【变量'{k}'】:\n    类型: {type(v)}\n    长度: {len(v)}\n    值: {v} \n\n")
        else:
            print(f"\n【变量'{k}'】:\n    类型: {type(v)}\n    长度: NAN\n    值: {v} \n\n")


def kkprint(**kwargs):
    """
        主要使用场景: 当爬虫接口中的json太长时候, 为了美化打印用的.
    """
    "方便打印出某些变量的值(测试使用); 需要使用关键字传参"
    json_ = json.dumps(kwargs, indent=4, ensure_ascii=False)
    print(json_)





def k_update(dic, key, value):
    "添加一个'k-v'对的同时, 返回这个添加后的dict对象!! (python默认是没有返回值的, 有些时候不方便) [下同]"
    dic[str(key)] = value
    return dic

def k_append(lst, element):
    lst.append(element)
    return lst

def k_extend(lst, lst2):
    lst.extend(lst2)
    return lst


def k_memory(obj, accuracy=False):
    """
        params:
            obj: 需要计算内存大小的对象
            accuracy: 是否需要精细测算内存大小 (使用递归的方法,把列表/字典中的元素全部遍历出来计算)

        return:
            memory_usage, unit

        note:
            getsizeof函数默认返回bytes(字节/大B)

        tips:
            比 df["<col>"].memory_usage(deep=True) 要稍大一丢丢 (但可以认为是相同的)
    """

    def recur_cal_memory(obj):
        "递归函数: 计算有深度的对象的内存"

        # 1. 列表对象
        if type(obj) == list:
            total_memory = 0
            for e in obj:
                memory_of_e = recur_cal_memory(e)
                total_memory += memory_of_e
            return total_memory

        # 2. 字典对象
        elif type(obj) == dict:
            total_memory = 0
            for k, v in obj.items():
                memory_of_k = sys.getsizeof(k)
                memory_of_v = recur_cal_memory(v)
                total_memory = total_memory + memory_of_k + memory_of_v
            return total_memory

        # 3. 其他
        else:
            # [递归的'原子条件': 当数据类型不为"list"和"dict"时]
            memory_usage = sys.getsizeof(obj)
            return memory_usage



    # 1. 需要精准计算
    if accuracy:
        memory_usage = recur_cal_memory(obj)

    # 2. 粗略计算即可
    else:
        memory_usage = sys.getsizeof(obj)

    # 以一种更"human"的方式呈现 '内存大小'
    if memory_usage < 1024:
        return round(memory_usage, 2), "Bytes"
    elif memory_usage < 1024*1024:
        return round(memory_usage/1024, 2), "KB"
    elif memory_usage < 1024*1024*1024:
        return round(memory_usage/1024/1024, 2), "MB"
    elif memory_usage < 1024*1024*1024*1024:
        return round(memory_usage/1024/1024/1024, 2), "GB"

def get_df_deep_memory(df):
    show_dict = {}
    columns = list(df.columns)
    for col in columns:
        # df[col].memory_usage(deep=True)
        memory_usage_tuple = k_memory(df[col])
        show_dict.update({col:memory_usage_tuple})
    kprint(show_dict=show_dict)
    return show_dict



def get_top(df, field_1, field_2, top_num=5, ascending=True):
    """
        function: 计算"某"个分类的"某"个字段的"前5名"
        params:
            df: 所需df
            field_1: 按它分类
            field_2: 按它排名
            top_num: 取前几名
    """
    # 先对df的 "field_2" 进行排序
    df = df.sort_values(field_2, ascending=ascending)

    # 用于计数的dict
    d = {}
    def foo(row):
        # nonlocal d
        """
            row: 是df中的一行
        """
        _key = row.get(field_1)
        if d.get(_key, 0) == 0:
            d.update({_key : 1})
            return row
        elif d.get(_key) < top_num:
            d.update({_key : d.get(_key) + 1})
            return row

    # 使用apply, 应用上面的函数
    df2 = df.apply(foo, axis=1)
    _ = df2.columns[0]
    df3 = df2.query(f"{_} == {_}")

    output_data(df3, f"top5_{field_2}")

    return df3


def base64_encrypt(data):
    """
    in:
        data: str类型 / bytes类型
    out:
        encrypted_b: bytes类型
    """
    # base64编码
    if type(data) == str:
        encrypted_b = base64.b64encode(data.encode('utf-8'))
    elif type(data) == bytes:
        encrypted_b = base64.b64encode(data)
    print(f"base64加密后的字节码: {encrypted_b}\n")
    return encrypted_b


def base64_decrypt(b):
    """
    in:
        b: bytes类型
    out:
        origin_s: str类型
    """
    # base64解码
    origin_s = base64.b64decode(b).decode("utf-8")
    print(f"base64解密后的'原始字符串': {origin_s}\n")
    return origin_s





class kwEncryption():
    "支持中文的AES加密!!(mode:CBC模式)"

    def __init__(self, key):
        """
        params:
            key: 必须是ascii字符 (不能是中文) (可以不要求16个字符, 因为后续会自动填充)

        function:
            1. 初始化 key值 和 iv值

        notes:
            1. key,iv使用同一个值
            2. key值和iv值必须要16个字节才行, 所以当key小于16位的时候, 使用"!"自动填充
        """
        # key 和 iv 使用同一个值
        key = key.ljust(16,'!')
        self.key = key
        self.iv = key
        self.key_bytes = bytes(key, encoding='utf-8')
        self.iv_bytes = bytes(key, encoding='utf-8')



    # 用于填充16位字节的辅助函数
    # (不太重要, 但必须要有. 其实可以直接写在底层,不需要自己造轮子啊....!!!贼烦)
    def pkcs7padding(self, text):
        """
        明文使用PKCS7填充
        最终调用AES加密方法时，传入的是一个byte数组，要求是16的整数倍，因此需要对明文进行处理
        :param text: 待加密内容(明文)
        :return:
        """
        bs = AES.block_size  # 16
        length = len(text)
        bytes_length = len(bytes(text, encoding='utf-8'))
        # tips：utf-8编码时，英文占1个byte，而中文占3个byte
        padding_size = length if(bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        # tips：chr(padding)看与其它语言的约定，有的会使用'\0'
        padding_text = chr(padding) * padding
        return text + padding_text
    def pkcs7unpadding(self, text):
        """
        处理使用PKCS7填充过的数据
        :param text: 解密后的字符串
        :return:
        """
        try:
            length = len(text)
            unpadding = ord(text[length-1])
            return text[0:length-unpadding]
        except Exception as e:
            pass


    def aes_encode(self, content):
        """
        function: AES加密
        参数:
            content: 待加密的内容(原内容)
        模式: cbc
        填充: pkcs7
        return:
            加密后的内容

        """
        cipher = AES.new(self.key_bytes, AES.MODE_CBC, self.iv_bytes)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        aes_encode_bytes = cipher.encrypt(bytes(content_padding, encoding='utf-8'))
        # 重新编码
        result = str(base64.b64encode(aes_encode_bytes), encoding='utf-8')
        return result


    def aes_decode(self, content):
        """
        function: AES解密
        参数:
            content: 加密后的内容
        模式: cbc
        去填充: pkcs7
        return:
            加密前的内容(原内容)
        """
        try:
            cipher = AES.new(self.key_bytes, AES.MODE_CBC, self.iv_bytes)
            # base64解码
            aes_encode_bytes = base64.b64decode(content)
            # 解密
            aes_decode_bytes = cipher.decrypt(aes_encode_bytes)
            # 重新编码
            result = str(aes_decode_bytes, encoding='utf-8')
            # 去除填充内容
            result = self.pkcs7unpadding(result)
        except Exception as e:
            raise Exception(f"该内容:'{content}', 无法被AES解密!!\n")
            # pass
        if result == None:
            return ""
        else:
            return result



# 测试:
# ==============
# 对中文加密
x = kwEncryption("kw618").aes_encode("萧山")
# 对中文解密
s = kwEncryption("kw618").aes_decode(x)





def task_01():
    print("\n\n\ntask正在执行....\n\n\n")


class TimerControler():
    def __init__(self, main_freq=8):
        pass
        """
        params:
            task_freq_table: 任务频次表  (记录每个对应时间的task执行次数)
                note:
                    1. 24-8: 包括24点, 也包括8点  (左右都能取到)
                    2. 使用分段的形式, 避免24个时间段的穷举法...(穷举有点low)

        """
        self.task_freq_table = {
            "24-8":0, "9-11":main_freq, "12-13":5, "14-18":main_freq, "19-21":5, "22-23":3
        }



    def get_task_freq(self, this_hour):
        """
        function:
            从原先的对应关系表中, 获取该小时中, task需要执行的次数!
        params:
            task_freq: 一小时中task需要执行的次数
        """
        if this_hour == 24 or this_hour <=8:
            task_freq = self.task_freq_table.get("24-8", 2)

        elif 9 <= this_hour <= 11:
            task_freq = self.task_freq_table.get("9-11", 2)

        elif 12 <= this_hour <= 13:
            task_freq = self.task_freq_table.get("12-13", 2)

        elif 14 <= this_hour <= 18:
            task_freq = self.task_freq_table.get("14-18", 2)

        elif 19 <= this_hour <= 21:
            task_freq = self.task_freq_table.get("19-21", 2)

        elif 22 <= this_hour <= 23:
            task_freq = self.task_freq_table.get("22-23", 2)

        print(f"\ntask_freq: {task_freq}\n")
        return task_freq




    def accumulate_lst(self, lst):
        """
        function: 计算一个list中的累计值
            eg:
                原lst:   [8, 4, 11, 9, 3, 8, 7, 7]
                累计lst:  [8, 12, 23, 32, 35, 43, 50, 57]
        """
        # lst = [8, 4, 11, 9, 3, 8, 7, 7]
        accumulated_lst = []
        for i in range(1, len(lst)+1):
            accumulated_lst.append(sum(lst[:i]))
        print(f"\naccumulated_lst: {accumulated_lst}\n")
        return accumulated_lst


    def get_minute_run_lst(self, task_freq=6, std_deviation=1):
        """
        params:
            std_deviation(标准差): 默认为3; 大概意思就是在均值的基础上上下浮动3
        """
        if task_freq != 0:
            avg_value = 60 / task_freq

            minute_array = np.random.normal(avg_value, std_deviation, task_freq)
            minute_array = [int(min) for min in minute_array] # 取整数
            print(f"\n 60分钟内的随机取数为: {minute_array}\n")
            minute_run_lst = self.accumulate_lst(minute_array)
            print(f"\nminute_run_lst: {minute_run_lst}\n")
            return minute_run_lst # [7, 17, 27, 37, 47, 57] (list)  (当lst中存在>=60的分钟数, 后续会被忽略, 不执行)
        else:
            return [999] # 当这个小时段不需要执行task的时候, 故意把"执行的实际分钟数调至999(最多是59)",即: 该小时不执行



    def run(self, task):
        """
            function:
                1. 根据任务执行频次表"", 定时执行task函数. (模拟人工审批, 以免被识别成是机器爬虫)
                2. run方法为该"时间控制器"的主入口

        """
        init = True
        while True:
            today_obj = pd.to_datetime("today")
            this_time = today_obj.strftime("%X")
            this_hour = int(this_time[0:2])
            this_minute = int(this_time[3:5])
            this_second = int(this_time[6:9])

            # 1. 每整小时执行一次: 重新执行一遍 "抽取随机分钟"
            if (this_minute == 0 and this_second == 0) or (init == True):
                if init == True:
                    init = False # 如果一开始执行的时候没有整点, 就只能通过这种方式产生"minute_run_lst"
                    print(f"初始化报时: {this_time}")
                    print("===========================================")
                    print("===========================================\n\n")
                else:
                    print(f"整小时报时: {this_time} ----------")
                    print("===========================================")
                    print("===========================================\n\n")
                task_freq = self.get_task_freq(this_hour)
                minute_run_lst = self.get_minute_run_lst(task_freq=task_freq)
                minute_run_lst.append(this_minute+1) # (当初始化执行的时候,需要马上执行)
                # 如果是59的话就不执行了, 防止task来不及执行完, 错过下一个整点的"抽取"机会....导致下一个小时段, 都没有新的"minute_run_lst"
                if 59 in minute_run_lst:
                    minute_run_lst.remove(59)
                print(f"\n\n【minute_run】【ALL】当前小时段的minute_run_lst: {minute_run_lst}\n\n")


            # 2. 每整分钟执行一次: 去run_time_lst中检查下, 当前分钟是否需要执行task
            if this_second == 0:
                print(f"\n整分钟报时: {this_time}\n")
                if this_minute in minute_run_lst.copy():
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>开始执行任务:")
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                    task() # 执行任务
                    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<任务执行结束;")
                    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                    minute_run_lst.remove(this_minute) # 执行完后, 把这个 minute_run 的时间给删掉 (防止同一分钟的不同秒中又会重复运行)
                    print(f"\n\n【minute_run】【剩余】当前小时段的minute_run_lst: {minute_run_lst}\n\n")

            time.sleep(1)

# 测试:
# ==============
# TC = TimerControler()
# TC.run(task_01)



def is_same_pos_neg(x, y):
    # 用于检测传入的x,y的数据类型
    if hassttr(x, "__neg__") and hassttr(y, "__neg__"):
        if x * y > 0:
            print("x与y, 同正负方向.\n")
            return True
        elif x * y < 0:
            print("x与y, 不同正负方向.\n")
            return False # 此时, 为'买卖点'
        elif x * y == 0:
            print("x与y, 其中有个为0.\n")
            return True # 主要用途是"量化中发生金叉/死叉时候判断买卖点, 为0时不执行买卖, 所以把它暂时视为True"
    else:
        raise(Exception("传入的x/y, 数据类型错误...\n"))





if __name__ == "__main__":
    m = 33
    n = 99
    kprint(m=m, n=n)
    TimerControler().get_minute_run_lst()








#
