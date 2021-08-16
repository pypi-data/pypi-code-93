#!/usr/bin/env python
# coding=utf-8
# 启动后台服务器的守护进程


import os
import sys
import time
import supervisor
PWD = os.path.dirname(os.path.abspath(__file__))

SERVICE_MAP = {
        "statistic"  : {"cmd": "python -u manage.py StatisticCron -c", "remark": "统计后台服务"},
        "ldap"       : {"cmd": "python3 -u manage.py ldap_server ", " remark": "ldap 服务"},
        "celery_task": {"cmd": "celery -A celery_app worker -l info -E", "remark": "celery 任务 服务"},
        "celery_cron": {"cmd": "celery -A celery_app worker -B -l info -Q cron", "remark": "celery 定时任务 服务"},
}

ACTION_LIST = ('stop', 'start', 'status', 'list', 'restart', 'log')


class DaemonService(object):

    def __init__(self, service_name):
        self.service_name = service_name
        self.service = SERVICE_MAP.get(service_name)

    def get_service_cmd(self):
        return self.service.get('cmd').strip()

    def get_service_pid(self):
        cmd = 'pgrep -f "%s"' % (self.service.get('pid_str', '') or self.get_service_cmd())
        return self.run_cmd(cmd)

    def check_runing_status(self):
        pids = self.get_service_pid()
        servce_status_str = '%s:[%s](%s) ' % (self.service_name, self.get_service_cmd(), self.service.get('remark', ''))
        if not pids:
            print('\033[31m%s not running!\033[0m' % servce_status_str)
        else:
            print('\033[32m%s running(%s)!\033[0m' % (servce_status_str, pids.replace('\n', ',')))
        return pids

    def service_status(self):
        return self.check_runing_status()

    def service_start(self):
        if not self.check_runing_status():
            is_nohup = self.service.get('nohup', True)
            cmd = self.get_service_cmd()
            if is_nohup:
                log_file_name = self.log_file_name
                cmd = 'nohup %s >> %s 2>&1 &' % (cmd, log_file_name)
            self.run_cmd(cmd)
            time.sleep(1)
            return self.check_runing_status()

    @property
    def log_file_name(self):
        return 'logs/%s_daemon.log' % self.service_name

    def service_log(self):
        print(self.log_file_name)
        os.system('tail -f %s' % self.log_file_name)

    def service_stop(self):
        pids = self.check_runing_status()
        if pids:
            for pid in pids.split('\n'):
                self.run_cmd('kill -9 %s' % pid)
            time.sleep(1)
            return self.check_runing_status()

    def service_restart(self):
        self.service_stop()
        self.service_start()

    def service_list(self):
        print('%s[%s] #%s' % (self.service_name, self.service.get('cmd'), self.service.get('remark')))

    def run_cmd(self, cmd_str):
        _r = os.popen(cmd_str)
        return _r.read().strip()

    def __call__(self, action_name):
        action_method = getattr(self, 'service_%s' % action_name, None)
        if not action_method:
            self.__class__.print_help()
        else:
            return action_method()

    @staticmethod
    def print_help():
        print('Usage: %s [%s] service_name' % (__file__,
                                               '|'.join(ACTION_LIST)
                                               ))


def read_parmas():
    import argparse
    argv = sys.argv
    if len(argv) >= 2:
        action = argv[1]
        if action in ACTION_LIST:
            if len(argv) >= 3:
                service_name = argv[2] if len(argv) >= 3 else ''
                if service_name in SERVICE_MAP:
                    daemon_service = DaemonService(service_name)
                    daemon_service(action)
                    return
                else:
                    action = 'list'

            for service_name in SERVICE_MAP:
                daemon_service = DaemonService(service_name)
                daemon_service(action)
        else:
            DaemonService.print_help()

    else:
        DaemonService.print_help()


if __name__ == '__main__':
    os.chdir(PWD)
    read_parmas()
