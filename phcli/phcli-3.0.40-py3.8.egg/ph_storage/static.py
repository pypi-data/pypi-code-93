# -*- coding: utf-8 -*-
import os

CLI_VERSION = "2020-08-10"

ASSUME_ROLE_ARN = 'YXJuOmF3cy1jbjppYW06OjQ0NDYwMzgwMzkwNDpyb2xlL1BoLUNsaS1MbWQ='
ASSUME_ROLE_EXTERNAL_ID = "Ph-Cli-Lmd"

BUCKET = "ph-platform"


def createDownLoadPath(local_storage, path):
    return local_storage.createDir((os.path.abspath('') + "/" + path).replace("//", "/"))


UPLOADPATH = CLI_VERSION + "/backups"

# HDFSPATH = ["hdfs://backup:8020/common/public/cpa/0.0.4/YEAR=2015.0/MONTH=2.0"]
