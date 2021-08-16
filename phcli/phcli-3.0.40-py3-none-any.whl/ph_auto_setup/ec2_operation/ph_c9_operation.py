import os
import json


class Phc9Operation(object):
    def __init__(self, **kwargs):
        self.c9_name = kwargs.get('name', None)

    def choice_operation(self):
        if self.ec2_operation == "create":
            Phc9Operation.create_c9(self)
        if self.ec2_operation == "delete":
            Phc9Operation.delete_c9(self)

    def create_c9(self):
        # 4.需要创建c9的用户
        users = self.c9_name.split(",")

        # 从ssm获取cluster_id
        cluster_id_cmd = "aws ssm get-parameter --name cluster_id"
        cluster_id_info = os.popen(cluster_id_cmd).readlines()
        cluster_id_str = ''.join(cluster_id_info)
        cluster_id_dict = json.loads(cluster_id_str)
        cluster_id = cluster_id_dict['Parameter']['Value']

        users_ip_cmd = "aws ssm get-parameter --name usersIp"
        users_ip_info = os.popen(users_ip_cmd).readlines()
        users_ip_str = ''.join(users_ip_info)
        users_ip_dict = json.loads(users_ip_str)
        users_ip = users_ip_dict['Parameter']['Value']
        users_ip_dict = json.loads(users_ip)

        # 5.创建ec2实例
        create_c9_cmd1 = "curl https://ph-platform.s3.cn-northwest-1.amazonaws.com.cn/2020-11-11/emr/common/client/cloud9cfn.yaml -o ./cloud9cfn.yaml"
        os.system(create_c9_cmd1)
        for user in users:
            user_ip = users_ip_dict.get(user, None)
            create_c9_cmd2 ="aws cloudformation create-stack --stack-name " + user + "-c9 " \
                                                                                           "--template-body file://cloud9cfn.yaml " \
                                                                                           "--parameters ParameterKey=EMRClusterId,ParameterValue=" + cluster_id + \
                                  " ParameterKey=EC2User,ParameterValue=" + user + \
                                  " ParameterKey=PrivateIpAddress,ParameterValue=" + user_ip
            os.system(create_c9_cmd2)
        create_c9_cmd3 = "rm -f cloud9cfn.yaml"
        os.system(create_c9_cmd3)


    def delete_c9(self):
        # 需要删除c9的用户
        users = self.c9_name.split(",")

        # 删除所有的c9实例
        for user in users:
            delete_c9_cmd = "aws cloudformation delete-stack --stack-name " + user + "-c9"
            os.system(delete_c9_cmd)