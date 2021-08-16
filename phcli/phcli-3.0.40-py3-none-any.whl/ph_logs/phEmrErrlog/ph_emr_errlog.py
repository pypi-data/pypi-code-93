import subprocess
import os
import sys
import json
import re
from phcli.ph_logs.phLogs.ph_logs import phlogger


class phErrLogs(object):
    
    def __init__(self,**kwargs):
        self.clusterId = kwargs.get('cluster_id',None)
        self.stepId = kwargs.get('step_id',None)
        self.fileName = kwargs.get('name',None)
      
     
    def extractlog(self):
        self.getLogByClusterAndstep()
        
             
    def getLogByClusterAndstep(self):
        JS_comm = "aws emr describe-step --cluster-id " + self.clusterId + " --step-id " + self.stepId
        JS_logs = os.popen(JS_comm)
        logs = JS_logs.read()
        log = json.loads(logs)
        applicationid = re.findall('application_\d*_\d*',logs)
        state = log["Step"]["Status"]["State"]
        if len(applicationid) > 0 :
            if state in "COMPLETED":
                phlogger.debug("集群ID或者步骤ID输入有误")
            else:
                log_path = "s3://ph-platform/2020-11-11/emr/yarnLogs/hadoop/logs-tfile/" + applicationid[0] + "/"
                comm_ls = "aws s3 cp --recursive " + log_path + " ./JS_log"
                if self.fileName is None:
                    os.popen(comm_ls + "&&" +"cat ./JS_log/*.compute.internal_8041" + " && " + "rm -rf ./JS_log",'w')   
                else:
                    cat_comm = "cat ./JS_log/*.compute.internal_8041 > " + self.fileName
                    os.popen(comm_ls + " && " + cat_comm + " && " + "rm -rf ./JS_log")
        self.getLogByAppLicationId()

                           
    def getLogByAppLicationId(self):
        stderr_path = "s3://ph-platform/2020-11-11/emr/logs/" + self.clusterId + "/" + "steps/" + self.stepId + "/"
        A_comm = "aws s3 cp --recursive " + stderr_path + " ./Application_log"
        gun_comm = "gunzip ./Application_log/stderr.gz"
        if self.fileName is None:     
            os.popen(A_comm +" && "+ gun_comm + " && " + "cat ./Application_log/stderr" + " && " + "rm -rf ./Application_log",'w')
        else:
            cat_comm = "cat ./Application_log/stderr >> " + self.fileName
            os.popen(A_comm +" && "+ gun_comm + " && " + cat_comm + " && " + "rm -rf ./Application_log")
            