# -*- coding: utf-8 -*-

import time
import datetime
import select
import sys
import os

from proc_mem_monitor import VERSION, DEFAULT_REFRESH_INTERVAL
from proc_mem_monitor.proc_mem_handler import get_mem_usages


def refresh_screen(hostname, total_mem, pattern):
    global rss_peak

    os.system('clear')
    print('Process Memory Monitor ' + VERSION + ' - ' + hostname + \
          ' Total system memory: ' + str(total_mem))
    last_udpated = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    print('Last refreshed at ', last_udpated)
    print('\n')

    mem_table_format = '{0:10s}|{1:10s}|{2:12s}|{3:20s}'
    print(mem_table_format.format('PID', 'CPU %', 'RSS GB', 'Command'))

    mem_usages = get_mem_usages(pattern)
    for k in mem_usages.keys():
        print(mem_table_format.format(k,  str(mem_usages[k]['cpu']), 
                                      str(mem_usages[k]['rss']), mem_usages[k]['cmd']))

        if k == 'rss_total' and mem_usages[k]['rss'] > rss_peak:
            rss_peak = mem_usages[k]['rss']

    print(mem_table_format.format('rss peak', '', str(rss_peak), ''))

    print('\n\nPress "q" followed by "enter" key to exit')


def start_nogui(hostname, total_mem, patterns):
    global rss_peak

    rss_peak = 0
    while True:
        input = select.select([sys.stdin], [], [], 1)[0]
        if input:
            value = sys.stdin.readline().rstrip()
 
            if (value == "q"):
                sys.exit(0)               
        else:
            refresh_screen(hostname, total_mem, patterns[0])
            time.sleep(1)
