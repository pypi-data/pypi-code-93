#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : tmp.py
# @Time    : 2021-06-10
# @Author  : Skypekey


import os
import sys


def get_info(args, logger):
    result = args.rsplit("%%%")[-1].split("/")[-1]
    info = result.split("###")[0]
    tellno = result.split("###")[1]
    for i in tellno.split(","):
        logger.info()
        os.system(f"/nms/sendmsg/sendmsg.sh {i} alerts '{info}'")


if __name__ == "__main__":
    info = "WARN%%%18772794%%%Information%%%Down (0)%%%应用组:(朱心谷、寻友旭)/湖南省国库支付系统::紧急::100.96.72.1_湖南省国库支付系统_电子凭证库- 业务应用app-1::第三>方业务@@@湘潭市国库(电子凭证库)业务端口无法访问::Down (0)###111,222,3333"
    # log_file = ""
    # logger = get_logger(log_file)
    if len(sys.argv) != 2:
        print(1111)
        # logger.error("参数")
    else:
        info = sys.argv[1]
        print(222222)
        # get_info(info)
