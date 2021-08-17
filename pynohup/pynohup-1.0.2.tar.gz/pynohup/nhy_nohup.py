#!/usr/bin/env python
# coding: utf-8
# @Time    : 2020-06-23 22:28
# @Author  : niuhanyang
# @File    : daemon_process.py
# @Desc    : 后台运行python文件类
import sys, os
import time


class Daemon:
    def __init__(self, target, args=(), kwargs=None, stdin='/dev/null', pid_file=None, stdout=None, stderr=None):
        '''
        :param target:执行的函数名
        :param args:执行函数的位置参数，没有参数可以不写
        :param kwargs:执行函数的关键字参数，没有参数可以不写
        :param stdin:后台执行标准输入,不用管它没用
        :param stdout:后台执行标准输出的文件名，也就是出错日志写到哪里,默认写到tmp目录下
        :param stderr:后台执行出错的文件名，也就是出错日志写到哪里，默认写到tmp目录下
        '''
        self.target = target
        self.args = args
        self.kwargs = kwargs if kwargs != None else {}
        self.__stdin = stdin
        self.__pid_file = pid_file
        self.__stdout = stdout if stdout else '/tmp/%s_out.log' % self.target.__name__
        self.__stderr = stderr if stderr else '/tmp/%s_err.log' % self.target.__name__

    def __daemonize(self):
        # 这个函数的实现是抄的，https://cloud.tencent.com/developer/article/1567443
        # 重定向标准文件描述符（默认情况下定向到/dev/null）
        try:
            pid = os.fork()
            # 父进程(会话组头领进程)退出，这意味着一个非会话组头领进程永远不能重新获得控制终端。
            if pid > 0:
                sys.exit(0)  # 父进程退出
        except OSError as e:
            sys.stderr.write("fork #1 failed: (%d) %s\n" % (e.errno, e.strerror))
            sys.exit(1)

            # 从母体环境脱离
        os.chdir("/")  # chdir确认进程不保持任何目录于使用状态，否则不能umount一个文件系统。也可以改变到对于守护程序运行重要的文件所在目录
        os.umask(0)  # 调用umask(0)以便拥有对于写的任何东西的完全控制，因为有时不知道继承了什么样的umask。
        os.setsid()  # setsid调用成功后，进程成为新的会话组长和新的进程组长，并与原来的登录会话和进程组脱离。

        # 执行第二次fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # 第二个父进程退出
        except OSError as e:
            sys.stderr.write("fork #2 failed: (%d) %s\n" % (e.errno, e.strerror))
            sys.exit(1)
        for f in sys.stdout, sys.stderr: f.flush()
        si = open(self.__stdin, 'r', encoding='utf-8')
        so = open(self.__stdout, 'a+', encoding='utf-8')
        se = open(self.__stderr, 'a+', encoding='utf-8')
        print('pid', os.getpid())
        self.__write_pid(os.getpid())
        os.dup2(si.fileno(), sys.stdin.fileno())  # dup2函数原子化关闭和复制文件描述符
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    def __write_pid(self, pid):
        if self.__pid_file:
            with open(self.__pid_file) as fw:
                fw.write(str(pid))

    def start(self):
        '''启动函数'''
        self.__daemonize()
        return self.target(*self.args, **self.kwargs)


def example(a, b, port=3306, country='china'):
    '''测试用的函数'''
    print(a, b, port, country)
    while True:
        time.sleep(1)
        print('example func')


if __name__ == '__main__':
    d = Daemon(target=example, args=(1, 2), kwargs={'country': 'japan'})
    d.start()
    # 运行完之后，会一直在后台运行这个python文件，请手动kill
