# -*- coding: utf-8 -*-

import subprocess
import os
import json
import shutil
import argparse
from pathlib import Path
import socket


from proc_mem_monitor.proc_mem_gui import start_gui
from proc_mem_monitor.proc_mem_nogui import start_nogui
from proc_mem_monitor import __resource_path__


def main():
    global prev_pattern, patterns, combo_pattern, root_window

    parser = argparse.ArgumentParser()
    parser.add_argument('--config-file', dest='config_file', default=None,
                        help='Specify a JSON file for getting the data')
    args = parser.parse_args()

    home = os.path.expanduser("~")
    user_config_file = home + '/proc-mem-monitor-config.json'
    default_config_file = __resource_path__ / 'proc-mem-monitor-config.json'
    if Path(user_config_file).exists():
        config_file = Path(user_config_file)
    elif default_config_file.exists():
        config_file = default_config_file

    with open(config_file, 'r') as fp:
        config_dict = json.load(fp)

    hostname = socket.gethostname()
    patterns = config_dict.get('patterns', [])
    
    # get total memory
    command = ['free', '-g']
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    free_out = p.stdout.read().decode('utf-8')
    mem_line = free_out.strip().split('\n')[1]
    total_mem = int(mem_line.split()[1])

    if os.environ.get('DISPLAY', None) is None:
        # no display start nogui version
        start_nogui(hostname, total_mem, patterns)
    else:
        start_gui(hostname, total_mem, patterns)


if __name__ == '__main__':
    main()



