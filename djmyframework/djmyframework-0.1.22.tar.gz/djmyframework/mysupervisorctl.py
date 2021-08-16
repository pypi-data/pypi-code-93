#!/usr/bin/env python
# coding=utf-8
# 启动后台服务器的守护进程


import copy
import os
import sys

pwd = os.getcwd()
sys.path.insert(0, pwd)
supervisor_config_dir = os.path.join(pwd, 'configfile')
from supervisor.options import ProcessConfig

supervisor_config_list = copy.copy(ProcessConfig.req_param_names)
default_supervisor_config = dict(
        command='{command}',
        directory='%(here)s/../../',
        priority='1',
        autorestart='false',
        redirect_stderr='true',
        stdout_logfile='logs/%(program_name)s.log',
        stdout_logfile_maxbytes='100MB',
        stdout_logfile_backups='10',
        stdout_capture_maxbytes='1MB',
        stderr_logfile='logs/%(program_name)s.error.log',
        stderr_logfile_maxbytes='100MB',
        stderr_logfile_backups='10',
        stderr_capture_maxbytes='1MB',
        stdout_events_enabled='false',
        loglevel='warn',
        stopsignal='TERM',
        #        killasgroup='true',
        #        stopasgroup='true'
)


def genrate_supervisor_conf(daemon_service_map, is_force=False):
    supervisor_config_ini_tpl = '''
# http://supervisord.org/configuration.html#program-x-section-values

[program:{name}]
process_name={name}
{program_config}
    '''

    supervisord_configs_dir = os.path.join(supervisor_config_dir, 'supervisord.conf.d')
    for name, config in daemon_service_map.items():

        config_file_path = os.path.join(supervisord_configs_dir, '%s.ini' % name)
        if config.pop('off', False):
            if os.path.isfile(config_file_path):
                print('the service %s is off remove configfile %s' % (name, config_file_path))
                os.remove(config_file_path)
            continue

        if not os.path.isfile(config_file_path) or is_force:
            if config.get('command', None) is None:
                raise Exception('[%s] Must be set command!' % name)
            supervisor_program_config = copy.copy(default_supervisor_config)
            supervisor_program_config.update(config)

            open(config_file_path, 'w').write(supervisor_config_ini_tpl.format(name=name, program_config='\n'.join(
                    ['%s=%s' % (k, v) for k, v in supervisor_program_config.items()])))


def main():
    supervisor_configfile = os.path.join(supervisor_config_dir, 'supervisord.ini')

    if not os.path.isfile(supervisor_configfile):
        raise Exception('%s not exists' % supervisor_configfile)
    from config.daemon_service import DAEMON_SERVICE_MAP, INET_HTTP_SERVER_LISTEN, INET_HTTP_SERVER_PASSWORD, \
        INET_HTTP_SERVER_USERNAME

    cmd = supervisorctl_cmd = 'supervisorctl -c %s' % (supervisor_configfile)
    os.environ.setdefault('INET_HTTP_SERVER_LISTEN', INET_HTTP_SERVER_LISTEN)
    os.environ.setdefault('INET_HTTP_SERVER_USERNAME', INET_HTTP_SERVER_USERNAME)
    os.environ.setdefault('INET_HTTP_SERVER_PASSWORD', INET_HTTP_SERVER_PASSWORD)
    os.environ.setdefault('PROJECT_ROOT', pwd)
    action = ''

    if len(sys.argv) > 1:
        action = sys.argv[1]
        if len(sys.argv) > 2:
            last_action = sys.argv[-1].strip()

            if last_action in ['log', 'restart', 'stop', 'start']:
                action = 'log'
                sys.argv.pop()

        if action == 'log':
            action = 'tail -f'
        # 改变 supervisorctl reload 为发送 重载信号到进程,实现平滑重启
        if action == 'reload':
            action = 'signal HUP'

        if action == 'reloadall':
            action = 'reload'
        argv_str = ' '.join(sys.argv[2:])
        cmd = '%s %s %s' % (supervisorctl_cmd, action, argv_str)

    genrate_supervisor_conf(DAEMON_SERVICE_MAP, is_force=action in ['update', 'nodaemon'])

    is_supervisord_running = os.system(supervisorctl_cmd + ' pid') == 0
    if not is_supervisord_running:
        print('supervisord not running !\nusage: mysupervisorctl [start|nodaemon] ')
        # -n/--nodaemon -- run in the foreground (same as 'nodaemon=true' in config file)
        if action == 'nodaemon':
            if not is_supervisord_running:
                argv = ['supervisord', '-c', supervisor_configfile, '-n']
                print(f'exec {" ".join(argv)} ')
                os.execvp('supervisord', argv)
            return
        if action == 'start':
            supervisord_cmd = 'supervisord -c %s' % supervisor_configfile
            print(supervisord_cmd)
            os.system(supervisord_cmd)
            return
        sys.exit(1)
    else:
        os.system(cmd)


if __name__ == '__main__':
    main()
