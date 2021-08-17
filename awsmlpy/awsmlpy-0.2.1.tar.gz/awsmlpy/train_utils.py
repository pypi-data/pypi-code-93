import boto3
import sagemaker
from sagemaker import get_execution_role
import json
import tarfile
import os
from time import gmtime, strftime

def train_own_docker_and_code(train_set_path, code_path, script, image, hyperparameters={}, role=None, prefix=None, bucket=None, sagemaker_session=None, instance_count=1, instance_type='ml.m5.xlarge'):
    
    # 创建tar.gz文件
    def create_tar_file(source_files, target=None):
        if target:
            filename = target
        else:
            _, filename = tempfile.mkstemp()

        with tarfile.open(filename, mode="w:gz") as t:
            for sf in source_files:
                # Add all files from the directory into the root of the directory structure of the tar
                t.add(sf, arcname=os.path.basename(sf))
        return filename
    
    # 超参数encode成json
    def json_encode_hyperparameters(hyperparameters):
        return {str(k): json.dumps(v) for (k, v) in hyperparameters.items()}
    
    def get_file_path(root_path):
        file_list = []
        for root, _, filenames in os.walk(root_path):
            for filename in filenames:
                file_list.append(os.path.join(root, filename))
        return file_list
    
    if type(prefix) == type(None):
        print('[WARNING] Did not specify prefix, so using default prefix awsml-training-job')
        prefix = 'awsml-training-job'
    
    # sagemaker_session
    if type(sagemaker_session) == type(None):
        print('[WARNING] Did not specify sagemaker_session, so trying to get default sagemaker_session:')
        sagemaker_session = sagemaker.session.Session()
        print('[WARNING] Geted sagemaker_session is : {}. This might be wrong, you can specify role using sagemaker_session=sagemaker.session.Session()'.format(sagemaker_session))
    
    # 把code的列表转换为具体的文件
    if not code_path.startswith('s3://'):
        print('[INFO] Uploading local code to S3')
        # 取得默认的bucket
        if not bucket:
            print('[WARNING] Parameter bucket is None, uploading local code to default S3 bucket: ', end='')
            bucket = sagemaker_session.default_bucket()
            print(bucket)
        print('[INFO] Uploading local code to default S3 bucket: s3://{}'.format(os.path.join(bucket, prefix, 'code')))
        
        code_files = get_file_path(code_path)
        
        # 把代码文件打包
        create_tar_file(code_files, "sourcedir.tar.gz")
        # 上传代码文件
        sources = sagemaker_session.upload_data("sourcedir.tar.gz", bucket, prefix + "/code")
        print('[INFO] Code file is uploaded to :{}'.format(sources))
    else:
        sources = code_files
    
    
    # 把代码的s3位置放进超参数
    hyperparameters['sagemaker_submit_directory']= sources
    # hyperparameter设置入口script
    hyperparameters['sagemaker_program'] = script
    # encode放入超参数
    hyperparameters = json_encode_hyperparameters(
        hyperparameters
    )
    
    # 如果没有role
    if not role:
        print('[WARNING] Didn\'t set excution role, so trying to get default excution Role')
        role = get_execution_role()
        print('[WARNING] Geted excution role is : {}. This might be wrong, you can specify role using role=\'ARN_ROLE\''.format(role))
    
    # 放入如下内容
    # docker ecr链接
    # role
    # 同时训练的数量
    # 机器类型
    # training jobs 前缀
    # 超参数
    print('*************************************\n' * 3)
    print('[INFO] Training image:', image)
    print('[INFO] Training role', role)
    print('[INFO] Code file list:', code_files)
    print('[INFO] Starting training')
    est = sagemaker.estimator.Estimator(
        image,
        role,
        instance_count=instance_count,
        instance_type=instance_type,
        # train_instance_type="local",
        base_job_name=prefix,
        hyperparameters=hyperparameters,
    )
    
    # 这个可以做映射的文件，假如有666，那么文件会被挂载到/opt/ml/input/data/666/
    est.fit({"train": train_set_path})
    return est