import base64
import json
import os

import boto3
import requests
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper

from savvihub.common.utils import read_in_chunks


class UploadableFileObject:
    def __init__(self, url, base_path, path):
        self.url = url
        self.base_path = base_path
        self.full_path = os.path.join(base_path, path)
        self.path = path

    def upload_chunks(self, *, callback=None):
        return read_in_chunks(self.full_path, callback=callback)

    def upload_hooks(self, *, callback=None):
        def fn(resp, **kwargs):
            if resp.status_code != 200:
                print(f'Upload for {resp.request.url} failed. Detail: {resp.data}')
        return {
            'response': fn,
        }

    def upload(self, session=requests.Session()):
        file_size = os.path.getsize(self.full_path)

        # send empty data when file is empty
        if os.stat(self.full_path).st_size == 0:
            future = session.put(
                self.url,
                data='',
                headers={'content-type': 'application/octet-stream'},
                hooks=self.upload_hooks(),
            )
            return future

        with open(self.full_path, "rb") as f:
            with tqdm(total=file_size, desc=self.path, unit="B", unit_scale=True, unit_divisor=1024) as t:
                wrapped_file = CallbackIOWrapper(t.update, f, "read")
                requests.put(self.url, data=wrapped_file)
        return


class UploadableS3MultipartFileObject:
    def __init__(self, bucket, key, local_path, token, part_size=int(15e6), verbose=False):
        self.bucket = bucket
        self.key = key
        self.path = local_path
        self.total_bytes = os.stat(local_path).st_size
        self.part_bytes = part_size
        self.token = token
        self.s3_client = self._get_s3_client_from_token()
        if verbose:
            boto3.set_stream_logger(name="botocore")

    def abort_all(self):
        mpus = self.s3_client.list_multipart_uploads(Bucket=self.bucket, Prefix=self.key)
        aborted = []
        if "Uploads" in mpus:
            for u in mpus["Uploads"]:
                upload_id = u["UploadId"]
                aborted.append(
                    self.s3_client.abort_multipart_upload(Bucket=self.bucket, Key=self.key, UploadId=upload_id))
        return aborted

    def create(self):
        mpu = self.s3_client.create_multipart_upload(Bucket=self.bucket, Key=self.key)
        mpu_id = mpu["UploadId"]
        return mpu_id

    def upload(self, mpu_id):
        parts = []
        uploaded_bytes = 0
        with open(self.path, "rb") as f:
            i = 1
            while True:
                data = f.read(self.part_bytes)
                if not len(data):
                    break
                part = self.s3_client.upload_part(
                    Body=data, Bucket=self.bucket, Key=self.key, UploadId=mpu_id, PartNumber=i)
                parts.append({"PartNumber": i, "ETag": part["ETag"]})
                uploaded_bytes += len(data)
                print(f"{self.path}: {uploaded_bytes} of {self.total_bytes} uploaded "
                      f"({(float(uploaded_bytes) / float(self.total_bytes) * 100.0):.3f}%)")
                i += 1
        return parts

    def complete(self, mpu_id, parts):
        result = self.s3_client.complete_multipart_upload(
            Bucket=self.bucket,
            Key=self.key,
            UploadId=mpu_id,
            MultipartUpload={"Parts": parts})
        return result

    def _get_s3_client_from_token(self):
        credentials = base64.b64decode(self.token).decode()
        credentials_dict = json.loads(credentials)
        return boto3.client(
            's3',
            aws_access_key_id=credentials_dict['AccessKeyId'],
            aws_secret_access_key=credentials_dict['SecretAccessKey'],
            aws_session_token=credentials_dict['SessionToken'],
        )


class DownloadableFileObject:
    def __init__(self, url, base_path, path, size=None):
        self.url = url
        self.full_path = os.path.join(base_path, path)
        self.size = size

    def download_hooks(self, *, callback=None):
        def fn(resp, **kwargs):
            os.makedirs(os.path.dirname(self.full_path), exist_ok=True)
            with open(self.full_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    if callback:
                        callback(chunk)
        return {
            'response': fn,
        }

    def download(self, session=requests.Session(), progressable=None):
        progress_callback = None
        if progressable and self.size:
            progress = progressable(length=self.size, label=self.full_path)
            progress_callback = lambda data: progress.update(len(data))

        future = session.get(
            self.url,
            stream=True,
            hooks=self.download_hooks(callback=progress_callback)
        )
        return future
