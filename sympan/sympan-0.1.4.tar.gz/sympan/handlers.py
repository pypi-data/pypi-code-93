import boto3
import os
import logging
from typing import Tuple, Optional
from joblib import Parallel, delayed

logger = logging.getLogger("Storage-Handler-SDK")
logger.setLevel(logging.DEBUG)

stdout_logger = logging.StreamHandler()
stdout_logger.setFormatter(
    logging.Formatter(
        '[%(name)s:%(filename)s:%(lineno)d] - [%(process)d] - %(asctime)s - %(levelname)s - %(message)s'
    )
)
logger.addHandler(stdout_logger)



class S3Handler:
    def __init__(self,
                 aws_access_key_id,
                 aws_secret_access_key,
                 region_name):

        self.s3 = boto3.resource('s3',
                                 aws_access_key_id=aws_access_key_id,
                                 aws_secret_access_key=aws_secret_access_key,
                                 region_name=region_name
                                 )

        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=aws_access_key_id,
                                      aws_secret_access_key=aws_secret_access_key,
                                      region_name=region_name)
    @staticmethod
    def get_bucket_name_and_key_from_s3_url(s3_url: str) -> Tuple[str, str]:
        path_with_bucket = s3_url.split('//')[1]
        path_with_bucket_splitted = path_with_bucket.split('/')
        bucket = path_with_bucket_splitted[0]
        if len(path_with_bucket_splitted) > 2:
            key = '/'.join(path_with_bucket.split('/')[1:])
            return bucket, key
        return bucket, ''

    def download_file(self,
                      bucket_name,
                      object_key,
                      local_filename):
        bucket = self.s3.Bucket(bucket_name)
        try:
            logger.info(f'Downloading file {object_key} from bucket {bucket_name} to {local_filename}')
            bucket.download_file(object_key, local_filename)
            logger.info('Download of the file is finished.')
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write(f'{bucket_name}, {object_key}\n')

            logger.error(f'Downloading file failed: {e}')

    def get_all_keys(self, bucket_name):
        bucket = self.s3.Bucket(bucket_name)
        for object in bucket.objects.all():
            key = object.key
            yield key

    def download_locally(self,
                         s3_url: str,
                         destination_folder: str,
                         n_jobs: Optional[int] = None):

        # create destination path if not present
        os.makedirs(destination_folder, exist_ok=True)

        # s3://bucket_name/source_key  this source_key is '' if s3_url is url bucket path
        bucket_name, source_key = S3Handler.get_bucket_name_and_key_from_s3_url(s3_url=s3_url)
        # if s3_url is not bucket path nor folder...that means it is some file with extension
        bucket_local_path = os.path.join(destination_folder, bucket_name)
        os.makedirs(bucket_local_path, exist_ok=True)

        if source_key != '' and not source_key.endswith('/'):
            # destination path with the same structure as the part in s3 before the file
            if '/' in source_key:
                base_destination_subfolder_key_path = os.path.join(bucket_local_path,
                                                                   os.sep.join(source_key.split('/')[:-1]))
                filename = source_key.split('/')[-1]
            else:
                base_destination_subfolder_key_path = bucket_local_path
                filename = source_key

            os.makedirs(base_destination_subfolder_key_path, exist_ok=True)

            print(filename)

            download_path = os.path.join(base_destination_subfolder_key_path, filename)
            if not os.path.exists(download_path):
                self.download_file(bucket_name=bucket_name,
                                   object_key=source_key,
                                   local_filename=download_path)


        elif source_key != '':  # the case when s3_url is not bucket path, but it is folder path inside bucket

            # build a folder with the same structure as source_key, but inside destination_folder

            # take all keys from bucket_name

            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket_name, Prefix=source_key)
            all_keys = []
            for page in pages:
                 for obj in page['Contents']:
                    all_keys.append(obj['Key'])


            def worker(key: str):
                # Exclude those keys that are folders or those files that don't contain source_key path
                if not key.startswith(source_key) or (key.startswith(source_key) and key.endswith('/')):
                    return None

                # download key locally
                base_destination_subfolder_key_path = os.path.join(bucket_local_path,
                                                                   os.sep.join(key.split('/')[:-1]))
                os.makedirs(base_destination_subfolder_key_path, exist_ok=True)
                filename = key.split('/')[-1]

                download_path = os.path.join(base_destination_subfolder_key_path, filename)
                if not os.path.exists(download_path):
                    self.download_file(bucket_name=bucket_name,
                                       object_key=key,
                                       local_filename=download_path)

            if n_jobs is not None:
                with Parallel(n_jobs=n_jobs, prefer="threads") as _parallel_pool:
                    _parallel_pool(delayed(worker)(key) for key in all_keys)
            else:
                for key in all_keys:
                    worker(key)
        else:  # the case when s3_url is bucket path

            all_keys = self.get_all_keys(bucket_name=bucket_name)

            def worker(key: str):
                print(key)
                # exclude subfolder keys..only use files with extension
                if key.endswith('/'):
                    return None
                # destination path with the same structure as the part in s3 before the file
                if '/' in key:
                    base_destination_subfolder_key_path = os.path.join(bucket_local_path,
                                                                       os.sep.join(key.split('/')[:-1]))
                    os.makedirs(base_destination_subfolder_key_path, exist_ok=True)
                    filename = key.split('/')[-1]
                else:
                    base_destination_subfolder_key_path = bucket_local_path
                    filename = key

                download_path = os.path.join(base_destination_subfolder_key_path, filename)
                if not os.path.exists(download_path):
                    self.download_file(bucket_name=bucket_name,
                                       object_key=key,
                                       local_filename=download_path)

            if n_jobs is not None:
                with Parallel(n_jobs=n_jobs, prefer="threads") as _parallel_pool:
                    _parallel_pool(delayed(worker)(key) for key in all_keys)
            else:
                for key in all_keys:
                    worker(key)