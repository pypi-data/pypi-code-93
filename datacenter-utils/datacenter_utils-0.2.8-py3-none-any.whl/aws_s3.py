# -*-coding:utf-8 -*-

"""
# File       : s3_file.py
# Time       ：2021/1/22 10:21 上午
# Author     ：shen
# version    ：python 3.7
# Description：
"""
import boto3
import re
import gzip
import os


def download_s3(filter_str,
                bucket,
                access_key_id,
                secret_access_key,
                local_root_path):
    s3 = boto3.resource(service_name='s3',
                        aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key,
                        region_name='cn-north-1')
    bucket = s3.Bucket(bucket)

    for bucket_object in bucket.objects.all():
        key = bucket_object.key
        if key[:len(filter_str)] == filter_str and 'xml.gz' in key:
            local_path = os.path.join(local_root_path, key)
            if os.path.exists(local_path):
                continue
            try:
                print('downloading ', key)
                bucket.download_file(key, local_path)
            except:
                path = '/'.join(key.split('/')[:-1])
                path_mk = os.path.join(local_root_path, path)
                print('mkdir ', path_mk)
                os.makedirs(path_mk)
                bucket.download_file(key, local_path)
            print(f'downloaded to {local_path}')


def s3_list(filter_str, bucket, aws_access_key_id, aws_secret_access_key):
    s3 = boto3.resource(service_name='s3',
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        region_name='cn-north-1')
    bucket = s3.Bucket(bucket)
    print(f'{filter_str}:')
    print(f'====================')
    for bucket_object in bucket.objects.all():
        key = bucket_object.key
        if key[:len(filter_str)] == filter_str:
            print(key)
    print(f'====================')


def un_gz(file_name):
    f_name = file_name.replace(".gz", "")
    if os.path.exists(f_name):
        return
    g_file = gzip.GzipFile(file_name)
    open(f_name, "wb+").write(g_file.read())
    return f_name


def run_unzip_file(file_path):
    # 解压缩gz文件 -> xml
    f1 = []
    r1 = []
    get_file_path(file_path, f1, r1, file_style='.*gz$')
    for r in f1:
        file_name = un_gz(r)
        if file_name:
            print(f'saved {file_name}')


def get_file_path(root_path, file_list, dir_list, file_style='.csv', dir_style=''):
    dir_or_files = os.listdir(root_path)
    dir_or_files = list(filter(lambda x: x[0] != '.', dir_or_files))
    for dir_file in dir_or_files:
        dir_file_path = os.path.join(root_path, dir_file)
        if os.path.isdir(dir_file_path):
            if dir_style in dir_file_path:
                dir_list.append(dir_file_path)
                get_file_path(dir_file_path, file_list, dir_list, file_style=file_style)
        else:
            if re.search(re.compile(file_style), dir_file_path):
                # if file_style in dir_file_path:
                file_list.append(dir_file_path)
