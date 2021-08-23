import os

LOG_PATH = "/var/log/pyprobe/"
CONFIG_PATH = "/etc/pyprobe/"

if os.getenv("DEV"):
    LOG_PATH = ""
    CONFIG_PATH = ""
