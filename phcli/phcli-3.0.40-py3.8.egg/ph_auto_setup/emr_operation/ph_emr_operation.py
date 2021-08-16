import os
import json
import time

class PhEmrOperation(object):
    def __init__(self, **kwargs):
        self.emr_name = kwargs.get('name', None)
        self.emr_operation = kwargs.get('operation', None)


    def choice_operation(self):
        if self.emr_operation == "create":
            self.create_emr()
        if self.emr_operation == "delete":
            self.delete_emr()


    def get_active_clusterId(self):
        # 获取clusterId
        ls_cmd = "aws emr list-clusters --active"
        cluster = os.popen(ls_cmd).readlines()
        cluster_str = ''.join(cluster)
        cluster_dict = json.loads(cluster_str)
        for emr in cluster_dict.get("Clusters", None):
            if emr.get('Name', None) == 'phdev':
                cluster_id = emr["Id"]
        return cluster_id


    def put_clusterId_to_ssm(self):
        cluster_id = self.get_active_clusterId()
        # 3.将获取的clusterId 写入到ssm中
        put_parameter_cmd = 'aws ssm put-parameter --name "cluster_id" --type String --overwrite --value ' + cluster_id
        os.system(put_parameter_cmd)


    def create_emr(self):
        create_cluster_cmd1 = "curl https://ph-platform.s3.cn-northwest-1.amazonaws.com.cn/2020-11-11/emr/common/client/emr.yaml -o ./emr.yaml"
        create_cluster_cmd2 = "aws cloudformation create-stack --stack-name "+ self.emr_name +" --template-body file://emr.yaml"
        os.system(create_cluster_cmd1)
        time.sleep(15)
        os.system(create_cluster_cmd2)
        create_cluster_cmd3 = "rm -f emr.yaml"
        os.system(create_cluster_cmd3)


    def delete_emr(self):
        delete_cluster_cmd = "aws cloudformation delete-stack --stack-name " + self.emr_name
        os.system(delete_cluster_cmd)