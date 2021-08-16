#!/usr/bin/env python
# coding:utf-8
# 邮件相关

import os
import time

# mailto_list=["2025096180@qq.com","yuki19890717@vip.qq.com","cannanyunying@163.com"]
mailto_list = ["2025096180@qq.com"]
mail_host = "smtp.exmail.qq.com"
mail_user = "xiezhaorong@guangka.com"  # 用户名
mail_pass = "zvU9pW5JbVX8nXG4"  # 口令
#mail_pass = "bzrifxisceqvbcec"
mail_postfix = "qq.com"  # 发件箱的后缀
smtp_port = 465
import smtplib

from email.mime.text import MIMEText
import threading
import queue
import traceback
import io


def get_trace_msg(is_log=False):
    '''跟踪消息
    '''
    fp = io.StringIO()
    traceback.print_exc(file=fp)
    message = fp.getvalue()
    del fp
    return message


try:
    from functools import wraps
except ImportError:
    from django.utils.functional import wraps

try:
    from .log import TimedRotatingLogger
except:
    from logging.handlers import TimedRotatingFileHandler
    import logging


    def TimedRotatingLogger(name):
        '''返回定时的日志记录
        '''
        log_format = '[%(asctime)s] - %(name)s - %(levelname)s - %(message)s'
        formatter = logging.Formatter(log_format)
        logging.basicConfig(format=log_format)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        file_ha = TimedRotatingFileHandler(os.path.join('', '%s.log' % name), when='h', interval=24, encoding='utf-8')
        file_ha.setLevel(logging.INFO)
        file_ha.setFormatter(formatter)
        logger.addHandler(file_ha)
        return logger

_log = TimedRotatingLogger('Mail')


def ThreadWarp(func):
    @wraps(func)
    def new_func(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()
        t.join()

    return new_func


def send_mail(name, sub, content, to_list=mailto_list):  # to_list：收件人；sub：主题；content：邮件内容
    global mail_host
    me = name + "<" + mail_user + "@" + mail_postfix + ">"  # 这里的hello可以任意设置，收到信后，将按照设置显示
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = sub  # 设置主题
    msg['From'] = me
    msg['To'] = ";".join(to_list)
    print(mail_host)
    try:
        s = smtplib.SMTP_SSL(host=mail_host,timeout=10,port=465)
        s.connect(mail_host)  # 连接smtp服务器
        s.login(mail_user, mail_pass)  # 登陆服务器
        s.sendmail(me, to_addrs=to_list, msg=msg.as_string())  # 发送邮件
        s.close()
        _log.info("%s send oK!" % str(to_list))
    except Exception as e:
        _msg = get_trace_msg()
        _log.info("send error  %s !" % _msg)


class MailPoll(threading.Thread):
    def __init__(self):
        super(MailPoll, self).__init__()
        self.setDaemon(True)
        self.mail_q = queue.Queue()
        self.__stop = False

    def send_mail(self, *args, **kw):
        self.mail_q.put((args, kw))

    def send_template_mail(self, template, dict_data):
        pass

    def stop(self):
        self.__stop = True
        _log.info('MailPoll stop!')
        self.join()

    def run(self):
        _log.info('MailPoll running!')
        while not self.__stop:
            args = self.mail_q.get()
            send_mail(*args[0], **args[1])
            time.sleep(0.01)


if __name__ == '__main__':
    m_p = MailPoll()
    m_p.start()
    m_p.send_mail('公共SDK统计出错', "公共SDK统计出错", "<a href='http://www.baidu.com'>百度</a>")
    time.sleep(5)
    m_p.send_mail('芒果f阿萨德', "test2", "<a href='http://www.baidu.com'>百度</a>")
    m_p.stop()
    #
    # # coding=utf-8
    #
    # import smtplib
    # from email.mime.text import MIMEText
    # from email.header import Header
    #
    # from_addr = 'whchen@qq.com'  # 邮件发送账号
    # to_addrs = '2025096180@qq.com'  # 接收邮件账号
    # qqCode = 'bzrifxisceqvbcec'  # 授权码（这个要填自己获取到的）
    # smtp_server = 'smtp.qq.com'  # 固定写死
    # smtp_port = 465  # 固定端口
    #
    # # 配置服务器
    # stmp = smtplib.SMTP_SSL(smtp_server, smtp_port)
    # stmp.login(from_addr, qqCode)
    #
    # # 组装发送内容
    # message = MIMEText('我是发送的内容', 'plain', 'utf-8')  # 发送的内容
    # message['From'] = Header("Python邮件预警系统", 'utf-8')  # 发件人
    # message['To'] = Header("管理员", 'utf-8')  # 收件人
    # subject = 'Python SMTP 邮件测试'
    # message['Subject'] = Header(subject, 'utf-8')  # 邮件标题
    #
    # try:
    #     stmp.sendmail(from_addr, to_addrs, message.as_string())
    # except Exception as e:
    #     print('邮件发送失败--' + str(e))
    # print('邮件发送成功')