import os
import sys
from retry import retry
import traceback
import pysnooper
import user_agent
import time
import random
import requests
import re
import json
import collections
import threading   # threading.Thread 为可使用的多线程的类！
import multiprocessing # multiprocessing.Process 为可使用的多进程的类！
from scrapy import Selector
from urllib import parse
import smtplib,uuid
from email.mime.text import MIMEText
import execjs
from copy import deepcopy
import redis
import socket
import websocket
import ssl

## exchange邮件发送相关的库包
from exchangelib import DELEGATE, Account, Credentials, Configuration, NTLM, Message, Mailbox, HTMLBody
from exchangelib.protocol import BaseProtocol, NoVerifyHTTPAdapter
import urllib3
urllib3.disable_warnings() # 可以避免老是报错...

from kw618.k_requests.abuyun_proxies import AbuyunProxies
from kw618.k_requests.selenium_login import get_one_cookie
from kw618.k_python.utils_python import *

from kw618._file_path import *
from kw618.settings import *


# 一个traceback的函数, 用于定位bug出现的位置 (防止except Exception as e中, 只报错, 不报位置...有点坑)
k_tb = traceback.format_exc
"""
    使用案例:
        try:
            1/0
        except:
            print(k_tb(10))  ## except中, 可以呈现详细的报错信息
"""



class CookiesPool():
    """
        function:
            封装一个操作redis的对象, 把列表/哈希表/集合等redis数据结构的 '增删改查' 写成统一的'实例方法接口'
            pool的数据结构: 使用队列结构 (先进的先出, 适合爬虫项目)
                            所以: add是加到右边最后一个元素; get是左边第一个元素; pop也是左边第一个元素
        note:
            1. pool_type的种类:
                1. list
                2. dict
                3. set
    """
    def __init__(self, pool_name, pool_type="list", redis_host="localhost", redis_port=6379, db=0, decode_responses=True, **kwargs):
        if db:
            kwargs["db"] = db
        if decode_responses:
            kwargs["decode_responses"] = decode_responses
        self.redis = redis.StrictRedis(host="localhost", port=6379, **kwargs)
        self.pool_name = pool_name
        self.pool_type = pool_type
        # 先清空redis中的这个'键' (如果已经存在某些数据, 可能数据类型会和后面操作的方式对不上而报错)
        self.redis.delete(self.pool_name)

    # 增:
    # =================
    def add(self, value, key="undefined"):
        if self.pool_type == "list":
            res = self.redis.rpush(self.pool_name, value)
        elif self.pool_type == "dict":
            res = self.redis.hset(self.pool_name, key, value)
        return res

    # 删:
    # =================
    def pop(self):
        if self.pool_type == "list":
            res = self.redis.lpop(self.pool_name)
        elif self.pool_type == "dict":
            res = "'dict'类型的pool没有pop方法;\n"
        return res

    def delete(self, key):
        if self.pool_type == "list":
            res = self.redis.lrem(self.pool_name, 1, key)
        elif self.pool_type == "dict":
            res = self.redis.hdel(self.pool_name, key)
        return res

    # 改:
    # =================
    pass


    # 查:
    # =================

    def get(self, key="undefined"):
        if self.pool_type == "list":
            res = self.redis.lindex(self.pool_name, 0)
        elif self.pool_type == "dict":
            res = self.redis.hget(self.pool_name, key)
        return res

    def values(self):
        if self.pool_type == "list":
            res = self.redis.lrange(self.pool_name, 0, -1)
        elif self.pool_type == "dict":
            # "dict类型的, 直接返回items字典"
            res = self.redis.hgetall(self.pool_name)
        return res

    def length(self):
        if self.pool_type == "list":
            res = self.redis.llen(self.pool_name)
        elif self.pool_type == "dict":
            res = len(self.redis.hvals(self.pool_name))
        return res

    def __str__(self):
        return str(self.values())

    def __repr__(self):
        "推荐用这个!"
        return str(self.values())


class myRequest():
    def __init__(self):
        self.name = "kerwin"
        self.session = requests.Session()


    def build_parameters(self, query_dict: dict):
        """
            function: 将dict格式的query, 转化成'name=kerwin&age=27'的str格式 (便于http传递)
        """
        keys = list(query_dict.keys())
        keys.sort()
        query_str = '&'.join([f"{key}={query_dict[key]}" for key in query_dict.keys()])
        return query_str

    # 所有请求都用这个接口！
    @log_error() # 记录报错内容 (双层装饰器)
    @retry(tries=3, delay=4, backoff=2, max_delay=8) # 这里的4次retry是正常的网络连接出错重试(不考虑反爬)
    # @pysnooper.snoop()
    def req(self, url, *, proxies=None, selector=False, auth=None, allow_redirects=True,
            data=None, selenium=False, req_method="get", is_obj=False, use_session=False,
            sleep_sec=None, other_headers={}, timeout=30, encoding=None, requests=requests,
            **kwargs):
        """
        params:
            data: dict类型
            other_headers: dict类型
            **kwargs:
                cookies: 可传入一个dict类型的cookies_dict  (前提: other_headers中不能有"cookie")



        note:
            1.所有请求都用这个通用接口(要做到普遍性)
            2.服务器连接类型的出错,可以直接用上面的retry.不需要在robust_req中考虑了!
            3. 默认情况只返回 res_obj.text 文本 (一般需要用到res_obj对象比较少见)
            4. verify的作用是: 表明在访问https协议的网址时, 是否需要验证服务器的 server's TLS certificate. requests库默认为True.
                有时候使用charles时候在用req访问 'https网址', 会报错: 服务器tls证书验证失败, 导致的SSLError(bad handshake)
            5. requests.get() 方法是默认允许 "重定向/跳转"的!!
                    so: 当需要禁止跳转的时候, 在get()方法中加入: allow_redirects=False

        tips:  res_obj.status_code 为200时再做后续处理？
        """

        headers = {
            "User-Agent": user_agent.generate_user_agent(),
            # "Host": "www.dianping.com",
            # "Referer": "http://price.ziroom.com",
            # "Cookie": "a=123;b=456;c=789",
        }
        # 0. 如果使用session，之后302跳转过程中的所有cookies，都会存储在这个 self.session中
            ### 上面的入参 requests=requests 是避免这里把全局变量requests给屏蔽掉了
        if use_session:
            requests = self.session

        # 1.添加其他必要的头部信息(包括cookies可以以{"Cookie":"a=123;b=456;c=789"}形式update进来)
        # cookies 也可以含在other_headers里面
        headers.update(other_headers)

        # 2.使用代理ip
        if proxies is not None:
            if proxies == "abuyun":
                proxies = AbuyunProxies.proxies
            elif proxies == "clash":
                proxies = {
                    # 代理设置: 如果要翻墙, 需要把端口号改成clash的端口号
                    "http" :"http://localhost:7890",
                    "https" :"https://localhost:7890",
                    # "http" :"socks5://127.0.0.1:7890",
                    # "https" :"socks5://127.0.0.1:7890",
                }
            elif proxies == "charles":
                proxies = {
                    # 代理设置: 如果要通过charles抓取python发出请求的数据包, 需要把端口号改成charles的端口号
                    # (1. clash设置成系统代理; 即: 除本机外的第一层全局代理; 所有浏览器/软件发出的请求都先经过clash代理)
                    # (2. charles需要设置成clash外的二层代理 [external proxy]; )
                    "http" :"http://localhost:8888",
                    "https" :"https://localhost:8888",
                    # "http" :"socks5://localhost:8889",
                    # "https" :"socks5://localhost:8889",
                }
        else:
            # 默认使用不使用代理
            proxies = {
                # 代理设置: 如果要翻墙, 需要把端口号改成clash的端口号 (这里的1080是以前ssr的端口)
                # "http" :"http://localhost:1080",
                # "https" :"https://localhost:1080"

                # 需要密码认证的代理:
                # "http" :"http://user:password@ip:port",

                # 也可以用socks协议的代理:
                # "http" :"socks5://user:password@ip:port",
                # "https" :"socks5://user:password@ip:port",

                # notice: 意味着 '左边的请求' 会使用 '右边的代理' 来访问

            }


        # 3. 设置其他'关键参数'的默认值
            # 这里设置不需要SSL认证...
        kwargs.setdefault('verify', False) # [超级重要]: 对于https请求, 很多时候需要SSL认证, 有时候没有认证就请求失败...很麻烦..



        # 4.开始发送req
        # print("\nreq 已发出。。\n")
        # logger.log(logging.DEBUG, "req 已发出..\n")
        if req_method == "get":
            res_obj = requests.get(url, headers=headers,proxies=proxies, auth=auth, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        # 下面的 data参数 必须要先用json.dumps()转成str后，才能发送请求！！！ //k200628: 不需要转成json啊, 直接用dict类型就能传入请求啊
        elif req_method == "post":
            res_obj = requests.post(url, headers=headers,proxies=proxies, data=data, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        elif req_method == "put":
            res_obj = requests.put(url, headers=headers,proxies=proxies, data=data, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        elif req_method == "delete":
            res_obj = requests.delete(url, headers=headers,proxies=proxies, data=data, timeout=timeout, allow_redirects=allow_redirects, **kwargs)
        else:
            msg = f"req_method未知: {req_method}; 请检查..."
            logger.log(40, msg)
        self.res_obj = res_obj

        # 5.修改需要的编码格式
        if encoding:
            res_obj.encoding = encoding

        # 6.当需要返回原始response对象的时候
        if is_obj:
            return res_obj
        else:
            res_text = res_obj.text

        # 7.当需要对页面进行解析的时候可以开启这段代码
        if selector:
            selector = Selector(text=res_text)
            return selector

        # 8.睡眠 (怕被反爬..)
        if sleep_sec:
            time.sleep(sleep_sec)

        # 9.返回文本string
        return res_text


    def get_session_cookies_dict(self):
        # 获取整个session中的所有cookies！！好用！！ (自动解析cookiejar成dict)
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def get_res_obj_cookies_dict(self):
        return requests.utils.dict_from_cookiejar(self.res_obj.cookies)




    # 该函数为每个网站自定义的部分,需要抓包,多测试,才能让req更贱稳健!
    def robust_req(self, url, proxies=None, selector=False, auth=None,
                    data=None, selenium=False, req_method="get",
                    sleep_sec=None, abnormal_num=0,
                    get_cookies=None, other_headers={}):
        """
        说明:
        1.该函数,可以自由定义.自己决定ip被封的判断条件.这样会使req更加稳健.
        2.该函数必须要起到分类response的功能.(即:必须要划分好准确的my_status)

        重点:
        返回的数据要有两个元素:
        1.目标对象   (具体是str还是json,视情况而定)
        2.my_status
        """

        res_txt = self.req(url, proxies=proxies, selector=selector, auth=auth,
                            data=data, selenium=selenium, req_method=req_method,
                            sleep_sec=sleep_sec, other_headers=other_headers)

        # to be deleted: my_retry 这样的写法好像很鸡肋,不规范!
        # 这个loads时候很容易出错,这边设置重试3次!
        # exec_str = "json.loads(res_txt, strict=False)"
        # res_dict = my_retry(exec_str, 4, error_txt="json数据格式转化")
        res_dict = json.loads(res_txt, strict=False)


        # print(res_dict)

        # if get_cookies:
        #     cookies = get_cookies() # 返回格式为dict

        # 此处为req使用代理ip的重试次数,下面的数字"3"可调!
        for retry_time in range(1, 3):
            # 1. response 为正常情况
            if res_dict.get("status", 0) == "1":
                # res_dict.update({"my_status":"ok"})
                print("\n楼盘数据获取成功\n")
                return res_dict, "ok"

            # 2. response 表示没有找到相关数据,可以把请求放入abandon集合
            elif res_dict.get("status", 0) == "7":
                print("\n没有此楼盘数据,可以abandon..\n")
                return res_dict, "abandon"

            # 如果response都不在上述判断中,则视为ip被封,更改ip代理,重新req一遍
            else:
                # if get_cookies:
                #     other_headers = get_cookies() # 返回格式为dict
                print("\nip被封，更换ip...\n")
                res_txt = self.req(url, proxies="abuyun", selector=selector, auth=auth,
                                    data=data, selenium=selenium, req_method=req_method,
                                    sleep_sec=0.05, other_headers=other_headers) # 使用代理的话不用睡眠很久的!
                # 这个loads时候很容易出错,这边设置重试3次!
                exec_str = "json.loads(res_txt, strict=False)"
                res_dict = my_retry(exec_str, 4, error_txt="json数据格式转化")


        # 如果经过上面多次循环req还是找不到一种""已知归属"",则返回ip错误
        return res_dict, "wrong"


def get_my_ip(option=None, proxies=None):
    "用来测试服务器观测到我的请求是来自哪个ip的"
    "与代理ip相关"
    req = myRequest().req
    api_url = 'http://pv.sohu.com/cityjson?ie=utf-8'
    res_text = req(api_url, proxies=proxies)
    res_text = re.findall(r'({[\s\S]+})', res_text)[0]
    print(res_text)
    res_dict = json.loads(res_text)
    if option == "ip":
        return res_dict.get("cip")
    elif option == "name":
        return res_dict.get("cname")
    else:
        return res_dict






def txt_2_html(txt):
    txt = txt.replace("\n", "<br>")
    txt = txt.replace(" ", "&nbsp;")
    txt = txt.replace("font:", "font ")
    txt = txt.replace("div:", "div ")
    txt = txt.replace("table:", "table ")
    txt = txt.replace("th:", "th ")
    txt_html = txt
    return txt_html






class kEmailSenderExchange():
    "使用outlook邮箱的那种模式发邮件"

    def __init__(self):
        #此句用来消除ssl证书错误，exchange使用自签证书需加上
        BaseProtocol.HTTP_ADAPTER_CLS = NoVerifyHTTPAdapter

        # 配置基本用户信息
        # self.user_name = "lvzc1"
        # self.password = "Lzc15168201914*"

        # self.user_name = "chenb"
        # self.password = "Zz00000000."

        self.user_name = "yangjj4"
        self.password = "Yangjiajing131#"
        self.email_domain = "ziroom.com"
        self.server_address = "zr-casc.ziroom.com"

        # 登录
        self.login()

    def login(self, user_name=None, password=None, email_domain=None, server_address=None):
        """后续应该建立异常捕获机制"""
        user_name = user_name if user_name else self.user_name
        password = password if password else self.password
        email_domain = email_domain if email_domain else self.email_domain
        server_address = server_address if server_address else self.server_address

        # 连接/登录 我的邮箱
        my_email_address = "{}@{}".format(user_name, email_domain)
        cred = Credentials(r'{}\{}'.format(email_domain, user_name), password)
        config = Configuration(server=server_address, credentials=cred, auth_type=NTLM)
        self.account = Account(
            primary_smtp_address=my_email_address, config=config, autodiscover=False, access_type=DELEGATE
        )
        print('我的邮箱已连接/登录...\n')


    def python_str_2_html_tag(self, message, **kwargs):
        # print(kwargs)
        message = message.replace("\n", "<br>")
        message = message.replace(" ", "&nbsp;")
        message = message.replace("font:", "font ")
        message = message.replace("div:", "div ")
        message = message.replace("table:", "table ")
        message = message.replace("th:", "th ")
        # message = message.replace('<tr>', '<tr align="center">')
        # message = message.replace('&lt;', '<')
        # message = message.replace('&gt;', '>')
        message = message
        return message


    def k_send_msg(self, message, subject_="无主题", receiver_lst=['15168201914@163.com'], need_to_conver_html=False, **kwargs):
        # 1. 把message先转换成能在浏览器正常显示的 html类型 的文本
        if need_to_conver_html:
            message = self.python_str_2_html_tag(message)

        # 2. 编辑邮件内容
        email_obj = Message(
            account=self.account,
            subject=subject_,
            body=HTMLBody(message),
            # to_recipients=[Mailbox(email_address=['365079025@qq.com'])]
            to_recipients = [Mailbox(email_address=receiver_address) for receiver_address in receiver_lst]
        )

        # 3. 发送邮件
            ### 随机睡眠: 防止被封
        random_time = random.random()*2
        print("发送邮件前，睡眠 {}  中。。。".format(random_time))
        time.sleep(random_time)
            ### 异常捕获
        try:
            x = email_obj.send()
            print("邮件发送成功！")
            return True
        except Exception as e:
            print(e)
            print("邮件发送失败！")
            return False










class kEmailSenderSmtp():
    "**使用中转模式发邮件"

    def __init__(self):
        # 发邮件相关参数
        self.sender='365079025@qq.com'
        # qq邮箱授权码
        self.password="rrtvphpkphylbgja"
        # 服务提供商的邮箱后缀??
        self.smtpsever='smtp.qq.com'
        # 端口号
        self.port=465
        # 链接服务器发送 (是个发送邮件的实例对象)
        self.smtp = smtplib.SMTP_SSL(self.smtpsever,self.port)
        # 登录
        self.login()

    def login(self):
        #登录
            ### 登录时候容易连接错误报错,应该捕获异常,并重新执行!
        try:
            for count in range(1, 4): # 尝试3次连续登录
                try:
                    print("正在 login 邮箱..")
                    self.smtp.quit() #1. 先退出连接
                    self.smtp.connect(self.smtpsever, self.port) #2. 再连接
                    self.smtp.login(self.sender, self.password)
                    print("邮箱 login 成功..")
                    break # 如果能正常登录, 则退出循环
                except Exception as e:
                    print("尝试第 {} 次login 邮箱..".format(count))
                    time.sleep(1)
                    print(e)
        except Exception as e:
            print(e)
            raise Exception("邮箱连续登录3次, 依旧出错...")


    def python_str_2_html_tag(self, message, **kwargs):
        # print(kwargs)
        message_html = message.replace("\n", "<br>")
        message_html = message_html.replace(" ", "&nbsp;")
        return message_html


    def k_send_msg(self, message, subject_="无主题", receiver_lst=['15168201914@163.com'], **kwargs):
        """
        in: 1. receiver_lst 接受者的邮箱
            2. message为需要发生邮件的正文内容
            3. subject 邮件显示中的第一栏（主题）

        notes:
            1. 这里传送进来的message中的\n换行是python语法中的，而如果要在前端html中展示换行，
                需要使用<br>,或者<div>等html标签

        tips:
            1. 字体大小
                最小： <font size="1">a</font>
                最大： <font size="6">a</font>
            2. 字体颜色
                字体红色： <font color="#ff0000"> a </font>
            3. 背景颜色
                背景颜色黄色：<span style="background-color: rgb(255, 255, 0);"> a </span>

        todo:
            想用**kwargs的关键词传参，来自动使某些需要的元素格式化（字体大小、颜色等）
        """

        # 1. 把msg先转换成能在浏览器正常显示的 html类型 的文本
        message_html = self.python_str_2_html_tag(message)

        # 2. 编辑邮件内容
        body = message_html # 正文内容
        msg=MIMEText(body,'html','utf-8') ## 使用html格式解析器
        msg['from'] = self.sender # 不加这行也可以发送，但是邮箱列表中没有发件人的头像和名称。
        msg['subject'] = subject_

        # 3. 发送邮件
            ### 随机睡眠: 防止被封
        random_time = random.random()*3
        print("发送邮件前，睡眠 {}  中。。。".format(random_time))
        time.sleep(random_time)
            ### 异常捕获
        for try_time in range(3):
            try:
                self.smtp.sendmail(self.sender, receiver_lst, msg.as_string())  #发送
                print("邮件发送成功！")
                return True
            except Exception as e:
                print(e)
                print("邮件发送失败！尝试重新login....")
                self.login()
        return False

    def quit(self):
        #关闭
        self.smtp.quit()



# sender1 = kEmailSenderExchange()
# sender1.k_send_msg("tt: exchange")
# sender2 = kEmailSenderSmtp()
# sender2.k_send_msg("tt: smtp")




















# def k_send_msg(message, subject_="无主题", receiver_lst=['365079025@qq.com'], **kwargs):
#
#     def python_str_2_html_tag(message, **kwargs):
#         # print(kwargs)
#         message_html = message.replace("\n", "<br>")
#         message_html = message_html.replace(" ", "&nbsp;")
#         return message_html
#
#
#     message_html = python_str_2_html_tag(message)
#
#     #发邮件相关参数
#     sender='365079025@qq.com'
#     # password="kwijdwfiqsajcajb"            #qq邮箱授权码
#     # password = "kodcgdnhvcxxbhcc"
#     password="rrtvphpkphylbgja"            #qq邮箱授权码
#     # receiver_lst = ['365079025@qq.com', "962600510@qq.com"]
#     if not receiver_lst:
#         receiver_lst = ['365079025@qq.com']
#     smtpsever='smtp.qq.com'
#     port=465
#
#     #编辑邮件内容
#     body = message_html # 正文内容
#     msg=MIMEText(body,'html','utf-8')
#     msg['from'] = sender # 不加这行也可以发送，但是邮箱列表中没有发件人的头像和名称。
#     msg['subject'] = subject_
#
#     #链接服务器发送
#     smtp = smtplib.SMTP_SSL(smtpsever,port)
#     # 登录时候容易连接错误报错,应该搞个try,捕获异常,并重新执行!
#     smtp.login(sender,password)                          #登录
#     """频繁登录，发送，退出？？？是不是得封装在一个类中会更好一些？？"""
#     """而且发送邮件的频率要限制一下，给一个随机睡眠吧。。。"""
#     random_time = random.random()*3
#     print("发送邮件前，睡眠 {}  中。。。".format(random_time))
#     time.sleep(random_time)
#     smtp.sendmail(sender, receiver_lst, msg.as_string())  #发送
#     smtp.quit()                                     #关闭
#     print("邮件发送完成！")
#
#
#     """
#     发送邮件的异常捕获机制要搞起来！！啥时候没发送成功自己要知道
#     """
#
#

# msg = 'name:aa\nage ： 99\n\n   hhh'
# k_send_msg(msg, receiver_lst=["lvzc1@ziroom.com"])
# sys.exit()







def _robust_req(url):
    """
    note:
        1.该下划线开头的robust_req,仅作为模板使用.
          以后可以在此基础上做局部修改,套用在其他项目上.
        2.此函数是在req的基础上做了定制化处理,
          考虑到多种可能的返回值,分流处理,稳定地得到最终需要的数据.
    """
    # 0. 先获取redis的连接对象
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    for retry_time in range(1, 4):
        try:
            # 1.正常发起req
            token = r.get("price_system:AccessToken")
            other_headers = {
                "Access-Token":token,
            }
            res_txt = req(url, other_headers=other_headers)
            res_dict = json.loads(res_txt, strict=False) # 此处,我知道正常情况他会返回json格式,才这么写(需要针对不同场景写)

            # 2.如果被反爬, cookies验证失败，重新获取cookies
            if res_dict.get("code", 0) == "40002":
                print("token验证失败，使用post模拟登陆，获取cookies....")
                token = PriceSysCookies().get_target_cookie()
                r.set("price_system:AccessToken", token)
                print("\n最新token:{}\n".format(token))
                other_headers = {
                    "Access-Token":token,
                }
                res_txt = req(url, other_headers=other_headers)
                res_dict = json.loads(res_txt, strict=False)
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> (以上是关于cookies的验证)

            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> (以下是关于response的分流处理)
            # 1..如果获取到的status字段=7,说明服务器没有找到我想要的数据,遗弃它
            if res_dict.get("status", 0) == "7":
                return {}, "abandon"
            # 2.如果获取到的status字段=5,说明发生其他问题,待处理
            elif res_dict.get("status", 0) == "5": #此处占坑,作为其他错误response的捕获#
                return {}, "failure"
            # 3.如果以上错误response都没捕获到,说明response正常,返回该正常的response
            else:
                return res_dict, "success" #"被期望"的正常情况#

        except Exception as e:
            print(e)
            ## 服务器确实只返回这样的数据,可能是被反爬了,也可能是发送给服务器的数据有问题
            ## (大概率是被反爬了:1.ip被封;2.cookies过期;3.headers/query缺失等)
            ## 需要在上面代码块重新调整"返回值的判断逻辑"!!
            print("response 非目标对象, 可能被反爬!")
            print("马上进行第 {} 次req重试\n[睡眠3秒]".format(retry_time))
            time.sleep(3)
            continue
        return {}, "error"


# 生产者
def k_produce(lst=[], queue_name="unnamed", sub_queue_name="", produce_type="init"):
    """
    获取需要爬取的所有id,清空并存入redis的待爬队列中
    """
    # 0. 先获取redis的连接对象
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    # 1. 先把传入的队列名称加上 ":" (方便后面redis中分级)
    if queue_name:
        queue_name += ":"
    if sub_queue_name:
        sub_queue_name += ":"


    # 2. 分流: 区分生产者类型
        ### 1. 清空原有e, 重新放入所有e
    if produce_type == "init":
        # 将lst中的所有 '元素' 放入待爬队列
        # 1. 先清空历史遗留的元素
        r.delete("{0}{1}pending_queue".format(queue_name, sub_queue_name))
        # 2. push所有元素
        if len(lst): # 如果lst没有元素,下面的lpush会报错
            r.lpush("{0}{1}pending_queue".format(queue_name, sub_queue_name), *lst)
        ### 2. 加入新的e
    elif produce_type == "add":
        if len(lst): # 如果lst没有元素,下面的lpush会报错
            r.lpush("{0}{1}pending_queue".format(queue_name, sub_queue_name), *lst)




def k_consume_pool(consume_func, queue_name="unnamed", sub_queue_name="", thread_num=5, time_sleep=0.3):
    """
    function: 使用多线程，消费redis队列中的所有内容
                (消费方式需用用consume_func函数来定义)
                (可以是发起req，也可以是其他操作...)

    既然是多线程,一般需要用for循环,循环生成线程.
    再把这些子线程统一append到一个t_pool中管理.
    join()用于主线程阻塞等待这些子线程
    """
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    #################################### 分割线 ##########################################
    def safety():
        """
        function: 确保不发生漏爬现象
        非常完整的req流程，可供多线程并发爬取，不会存在抢占资源的问题
        """

        # 如果待爬队列有元素,就一直循环爬取
        while r.llen("{0}{1}pending_queue".format(queue_name, sub_queue_name)):
            num = r.llen("{0}{1}pending_queue".format(queue_name, sub_queue_name))
            print("待爬队列中的剩余元素量:{}\n".format(num))
            # 1.从待爬队列获取出e
            e = r.rpop("{0}{1}pending_queue".format(queue_name, sub_queue_name))
            # 2.将 e 放入error_queue
            r.lpush("{0}{1}error_queue".format(queue_name, sub_queue_name), e)

            try:
                # 3.真正执行任务的函数！！！（消费者函数）
                consume_func(e)
                # 4.将成功爬取的url存入已爬队列
                r.sadd("{0}{1}crawled_queue".format(queue_name, sub_queue_name), e)
                # 5.删掉错误队列中的响应元素
                r.lrem("{0}{1}error_queue".format(queue_name, sub_queue_name), -1, e)

            # 发送req后,不管出现什么问题,都把url遗留在error_queue中
            except Exception as e:
                print(e)
                tb_txt = traceback.format_exc(limit=5)
                print(tb_txt)
                # 如果req访问出错,数据获取失败,不管什么原因,把这个错误id遗留在错误队列中
                print("e={} 访问出错,遗留在错误队列中\n\n".format(e))
    #################################### 分割线 ##########################################

    # 1. 先把传入的队列名称加上 ":" (方便后面redis中分级)
    if queue_name:
        queue_name += ":"
    if sub_queue_name:
        sub_queue_name += ":"

    # 2.
    t_pool = []
    for _ in range(thread_num): # 此处创建5个线程来消费
        print("\n即将生成一个线程...")
        time.sleep(time_sleep)
        t = threading.Thread(target=safety)
        t.start()
        t_pool.append(t)
    for t in t_pool:
        t.join() # 主线程需要阻塞等待每一个子线程



def k_error_to_pending(queue_name):
    """
    function : 把error队列的数据转移到待爬队列中,便于开始对error的req重新爬取
    """
    # 0. 获取redis的连接对象
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

    # 1. 翻转error队列
    error_lst = r.lrange("{0}:error_queue".format(queue_name), 0, -1)
    error_lst.reverse()

    # 2. 把error队列中的错误元素, 倾倒入待爬队列中
    if len(error_lst): # 如果lst没有元素,下面的lpush会报错
        r.lpush("{0}:pending_queue".format(queue_name), *error_lst)
    # 3. 删除error队列
    r.delete("{0}:error_queue".format(queue_name))


def kill_error_queue(queue_name):
    "清空 error_queue 的元素"
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
    r.delete("{queue_name}:error_queue".format(queue_name=queue_name))


def k_crawl_error_again(queue_name, consume_func, thread_num=1, time_sleep=1, try_loops=1):
    "如果有错误req导致error_queue有留存元素,将其倒入pending_queue队列,重新对该部分爬取"
    r = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
    for try_times in range(try_loops): # 重试2次
        # 如果error_queue队列中已经没有元素,则跳出循环
        error_lst = r.lrange("adjust_price:error_queue", 0, -1)
        if len(error_lst) == 0:
            break
        # 否则倾倒队列,重新生成多线程消费者消费
        k_error_to_pending(queue_name=queue_name)
        k_consume_pool(queue_name=queue_name, consume_func=consume_func, thread_num=thread_num, time_sleep=time_sleep)



def get_js_txt_for_encrypt(js_full_path):
    """
    in: js代码的完整路径
        （经过自己过滤处理后，把所有可能用到的加密js函数全放在这个js文件中即可！！）
        必须要有个直接调用加密的函数
            eg.
            function encryptByDES(message, key) {.....}

    note:
        其实只要找到所有需要的js文件，直接复制、粘贴过来，都不需要修改什么，直接就可以用了诶！！！
        目前的难点是：1. 如何找到加密函数？   2. 如何把与加密相关的所有js文件都集齐、汇总到本js文件中
        难点1的思路：
            1. 使用事件断点：  click、xhr、encode解析、submit 等等
            2. 直接搜索关键词： encrypt, aes, submit, request, click, password, user, passpd, log, login
            3. 针对登录的form、输入密码的input等标签，后续js加密代码肯定需要使用这个标签获取这个input中的值，所以可以搜这个tag的id或类名
            4. 设置很多可能的断点，逐行逐行调试。配合使用堆栈的记录功能，快速跳转函数。(时刻关注local的变量值的变化)
        难点2的思路：
            1. 多配合"step into next function call" 的调试方式（可以下钻到更深一层的函数）
    """
    with open(js_full_path, "r", encoding="utf8") as file:
        js_txt = file.read()
    return js_txt




def exec_js_function(js_full_path, func_name, *args):
    """
    function: 获取js代码的上下文，指定某个js函数，并传入相应个数的参数，得到js函数的返回值
    参数说明:
        1.解密js的完整路径
        2.所使用的函数
        3+.可以传入多个参数
    """
    # print(args)
    # print("---\n\n")
    # print(*args)
    js_txt = get_js_txt_for_encrypt(js_full_path)
    ctx = execjs.compile(js_txt, f"{FILE_PATH_FOR_HOME}/node_modules")
    result = ctx.call(func_name, *args)
    return result


# 测试一 : 价格系统
# js_full_path = "/Users/kerwin/MyBox/MyCode/Personal/django_test01/first_project/static/js/encryption_4_price_system.js"
# a = exec_js_function(js_full_path, "encryptByDES", "Lzc15168201914*", "#z@i!r*o%o&m^")
# print(a)
# 测试二 : 内网（库存系统）
# js_full_path = "/Users/kerwin/MyBox/MyCode/Personal/django_test01/first_project/static/js/encryption_4_ziroom_intranet.js"
# a = exec_js_function(js_full_path, "encodeAes", "Lzc15168201914*")
# print(a)
# sys.exit()




# def k_urlEncode(txt):
def url_encode(txt):
    "url编码: 网络请求中特有'编码格式'(区别于unicode);"
    "正常来说, http/s请求的时候, 会自动把中文进行url编码; 但有时候, 需要我们手动对url进行编码, 所以写了个k接口"
    return parse.quote(txt)

# def k_urlDecode(txt):
def url_decode(txt):
    "url解码: 把%E6%9c%88 解码成 '月' "
    return parse.unquote(txt)






def main():
    # url = "https://www.amap.com/service/poiTipslite?&city=330100&type=dir&words={}".format("芳满庭")
    # res_txt = myRequest().robust_req(url)
    # print(res_txt)
    # print(dir())
    # print(__file__)
    # print(locals())
    print("ssssssssss"*88)





if __name__ == '__main__':
    print("start test!")
    main()
    print("\n\n\neverything is ok!")
