import os
import json


class PhJupyterOperation(object):
    def __init__(self, **kwargs):
        self.jupyter_name = kwargs.get('name', None)

    def choice_operation(self):
        if self.ec2_operation == "create":
            PhJupyterOperation.create_jupyter(self)
        if self.ec2_operation == "delete":
            PhJupyterOperation.delete_jupyter(self)

    def create_jupyter(self):
        # 4.需要创建jupyter的用户
        users = self.jupyter_name.split(",")

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
        create_jupyter_cmd1 = "curl https://ph-platform.s3.cn-northwest-1.amazonaws.com.cn/2020-11-11/emr/common/client/jupyterec2cfn.yaml -o ./jupyterec2cfn.yaml"
        os.system(create_jupyter_cmd1)
        for user in users:
            user_ip = users_ip_dict.get(user, None)
            create_jupyter_cmd2 = "aws cloudformation create-stack --stack-name " + user + "-jupyter " \
                                                                                           "--template-body file://jupyterec2cfn.yaml " \
                                                                                           "--parameters ParameterKey=EMRClusterId,ParameterValue=" + cluster_id + \
                                  " ParameterKey=EC2User,ParameterValue=" + user + \
                                  " ParameterKey=PrivateIpAddress,ParameterValue=" + user_ip
            os.system(create_jupyter_cmd2)
        create_jupyter_cmd3 = "rm -f jupyterec2cfn.yaml"
        os.system(create_jupyter_cmd3)


    def delete_jupyter(self):
        # 需要删除jupyter的用户
        users = self.jupyter_name.split(",")

        # 删除所有的jupyter实例
        for user in users:
            delete_jupyter_cmd = "aws cloudformation delete-stack --stack-name " + user + "-jupyter"
            os.system(delete_jupyter_cmd)