import subprocess
import os
import json
from phcli.ph_auto_setup.emr_operation.ph_emr_operation import PhEmrOperation

class PhEC2Init(object):

    def init_conf():
        # 获取cluster_id
        cluster_id = PhEmrOperation().get_active_clusterId()

        # 下载需要初始化的文件
        hadoop_cmd1 = "aws s3 cp s3://ph-platform/2020-11-11/emr/remoteConfig/" + cluster_id + "/etc/hadoop/conf/ hadoop/conf/ --recursive"
        hadoop_cmd2 = "sudo cp hadoop/conf/* /etc/hadoop/conf/"
        spark_cmd1 = "aws s3 cp s3://ph-platform/2020-11-11/emr/remoteConfig/" + cluster_id + "/etc/spark/conf/ spark/conf/ --recursive"
        spark_cmd2 = "sudo cp spark/conf/* /etc/spark/conf/"
        hive_cmd1 = "aws s3 cp s3://ph-platform/2020-11-11/emr/remoteConfig/" + cluster_id + "/etc/hive/conf/ hive/conf/ --recursive"
        hive_cmd2 = "sudo cp hive/conf/* /etc/hive/conf/"
        hive_hcatalog_cmd1 = "aws s3 cp s3://ph-platform/2020-11-11/emr/remoteConfig/" + cluster_id + "/etc/hive-hcatalog/conf/ hive-hcatalog/conf/ --recursive"
        hive_hcatalog_cmd2 = "sudo cp hive-hcatalog/conf/* /etc/hive-hcatalog/conf/"
        tez_cmd1 = "aws s3 cp s3://ph-platform/2020-11-11/emr/remoteConfig/" + cluster_id + "/etc/tez/conf/ tez/conf/ --recursive"
        tez_cmd2 = "sudo cp tez/conf/* /etc/tez/conf/"
        cmd = hadoop_cmd1 + " && " + hadoop_cmd2 + \
              " && " + spark_cmd1 + " && " + spark_cmd2 + \
              " && " + hive_cmd1 + " && " + hive_cmd2 + \
              " && " + hive_hcatalog_cmd1 + " && " + hive_hcatalog_cmd2 + \
              " && " + tez_cmd1 + " && " + tez_cmd2
        subprocess.call(cmd, shell=True)

        # 复制成功后删除当前目录下的文件
        rm_hadoop_cmd = "sudo rm -rf hadoop"
        rm_spark_cmd = "sudo rm -rf spark"
        rm_hive_cmd = "sudo rm -rf hive"
        rm_hive_hcatalog_cmd = "sudo rm -rf hive-hcatalog"
        rm_tez_cmd = "sudo rm -rf tez"

        rm_cmd = rm_hadoop_cmd + " && " + rm_spark_cmd + \
              " && " + rm_hive_cmd + " && " + rm_hive_hcatalog_cmd + \
              " && " + rm_tez_cmd
        subprocess.call(rm_cmd, shell=True)

        # 下载config.json文件
        cp_configJson_cmd = "sudo curl https://ph-platform.s3.cn-northwest-1.amazonaws.com.cn/2020-11-11/emr/remoteConfig/"+ cluster_id +"/sparkmagic/config.json -o /home/hadoop/.sparkmagic/config.json"
        subprocess.call(cp_configJson_cmd, shell=True)