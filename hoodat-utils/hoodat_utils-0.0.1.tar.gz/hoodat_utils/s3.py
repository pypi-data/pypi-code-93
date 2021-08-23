#####################################################
#           Imports                                 #
#####################################################

import os
import boto3
import logging

#####################################################
#           Functions                               #
#####################################################


class s3_data():
    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key
        self.client = boto3.client("s3",
                                   aws_access_key_id=self.access_key,
                                   aws_secret_access_key=self.secret_key)

    def list_dir(self, bucket, path, keys_only=True):
        paginator = self.client.get_paginator('list_objects')
        pageresponse = paginator.paginate(Bucket=bucket,
                                          Prefix=path,
                                          Delimiter="/")
        # PageResponse Holds 1000 objects at a time and will
        # continue to repeat in chunks of 1000.
        file_list = []
        for pageobject in pageresponse:
            for file in pageobject["Contents"]:
                if keys_only:
                    file_list.append(file["Key"])
                else:
                    file_list.append(file)
        return file_list

    def download_dir(self, region, bucket, s3_loc, save_loc):
        resource = boto3.resource("s3",
                                  aws_access_key_id=self.access_key,
                                  aws_secret_access_key=self.secret_key,
                                  region_name=region)
        paginator = self.client.get_paginator('list_objects')
        pageresponse = paginator.paginate(Bucket=bucket,
                                          Prefix=s3_loc,
                                          Delimiter="/")
        logging.info("checkpoint a")
        for pageobject in pageresponse:
            logging.info("checkpoint a2")
            if pageobject.get('CommonPrefixes') is not None:
                logging.info("checkpoint b")
                for subdir in pageobject.get('CommonPrefixes'):
                    self.download_dir(
                        # client, resource, subdir.get('Prefix'), save_loc, bucket
                        region,
                        bucket,
                        s3_loc,
                        save_loc)
            if pageobject.get('Contents') is not None:
                logging.info("checkpoint c")
                for file in pageobject.get('Contents'):
                    file_name = file.get("Key").replace(s3_loc, "")
                    save_path = os.path.normpath(save_loc) + os.sep + file_name
                    save_dir = os.sep.join(save_path.split(os.sep)[:-1])
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    resource.meta.client.download_file(bucket, file.get('Key'),
                                                       save_path)

    def upload_dir(self, bucket, local_dir, s3_loc):
        # enumerate local files recursively
        for root, dirs, files in os.walk(local_dir):
            for filename in files:
                # construct the full local path
                local_path = os.path.join(root, filename)
                # construct the full s3 path
                relative_path = os.path.relpath(local_path, local_dir)
                s3_path = os.path.join(s3_loc, relative_path)
                logging.info('Searching {0} in {1}'.format(s3_path, bucket))
                try:
                    self.client.head_object(Bucket=bucket, Key=s3_path)
                    logging.info(
                        "Path already found on S3. Skipping {0}...".format(
                            s3_path))
                except:
                    logging.info("Uploading {0}...".format(s3_path))
                    self.client.upload_file(local_path, bucket, s3_path)
        logging.info("Upload complete")

    def download_file(self, bucket, s3_loc, save_loc):
        file_list = self.client.download_file(bucket, s3_loc, save_loc)
        return file_list

    def upload_file(self, bucket, s3_loc, local_loc):
        file_list = self.client.upload_file(local_loc, bucket, s3_loc)
