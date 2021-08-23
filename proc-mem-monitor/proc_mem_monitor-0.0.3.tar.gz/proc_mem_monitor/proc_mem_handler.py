# -*- coding: utf-8 -*-

import subprocess
import json
import re

def get_mem_usages(pattern, host='localhost'):
    ps_command = ['ps', 'ax', '--sort', '-rss', '-o', 'pid,%cpu,rss,cmd']
    if host == 'localhost':
        # ps -o pid,rss,cmd 273899
        command =  ps_command
    else:
        command = ['ssh', host] + ps_command

    #print('command=', command)
    #print('pattern', pattern)
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ps_dump = p.stdout.read().decode('utf-8')
    #print(ps_dump)
    ps_lines = ps_dump.strip().split('\n')
    rss_total = 0
    mem_usage_dict = {}
    re_pattern = re.compile(pattern)
    for l in ps_lines[1:]:
        #print('line', l)
        ps_fields = l.split()
        pid = ps_fields[0]
        cpu = ps_fields[1]
        rss = int(ps_fields[2])
        cmd = ps_fields[3]
        #print(pattern, cmd, re_pattern.search(cmd))
        if bool(re.search(pattern, cmd)):
            mem_usage_dict[pid] = {'cpu': cpu, 'rss': rss/1000000, 'cmd': cmd}

            #print('mem_usage_dict pid ', pid, mem_usage_dict[pid])
            rss_total = rss_total + rss

    mem_usage_dict['rss_total'] = {'cpu': '', 'rss': rss_total/1000000, 'cmd': ''}
    #print(mem_usage_dict)
    return mem_usage_dict

