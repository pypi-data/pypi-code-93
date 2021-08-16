import boto3

s3_bucket_name = "ph-apis"

def role_part():
    s3_file_path = "template/trust-policy.json"

    # with open ("../file/trust-policy.json", "r") as myfile:
    #     loads = json.load(myfile)
    #     print(loads)

    s3 = boto3.client('s3')
    object = s3.get_object(Bucket=s3_bucket_name, Key=s3_file_path)
    str = object["Body"].read().decode('utf-8')
    # str = json.load(object.get()["Body"])
    #
    client = boto3.client('iam')
    resp = client.create_role(RoleName='python-lambda-example-role2', AssumeRolePolicyDocument=str)
    print(resp)

    # iam = boto3.resource('iam')
    # role = iam.Role('python-lambda-example-role2')
    # print(role)
    # print(role.assume_role_policy_document)
    # policy_iterator = role.policies.all()
    # for policy in policy_iterator:
    #     print(policy)

# role_part()


def s3_part():
    s3_file_path = "template/trust-policy.json"
    s3 = boto3.resource('s3')

    # 列出所有库
    # for bucket in s3.buckets.all():
    #     print(bucket.name)

    # 上传文件
    data = open('../../file/ph_lmd/trust-policy.json', 'rb')
    s3.Bucket(s3_bucket_name).put_object(Key=s3_file_path, Body=data)
# s3_part()


def api_gateway_part():
    client = boto3.client('apigateway')

# api_gateway_part()

print("nodejs 支持")
print("项目移植")
print("进度，日志记录，回滚，接续执行")
print("保证版本一致性，可随时切换回来")
print("生成一份执行文件到s3")
