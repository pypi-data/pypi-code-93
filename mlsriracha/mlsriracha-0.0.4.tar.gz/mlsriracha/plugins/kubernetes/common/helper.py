import boto3
import os
from urllib.parse import urlparse
from pathlib import Path

def s3_download(s3_uri, download_path):
    # https://stackoverflow.com/questions/42641315/s3-urls-get-bucket-name-and-path
                    
    url = urlparse(s3_uri, allow_fragments=False)

    bucket = url.netloc
    path = url.path.lstrip('/')
    #  https://stackoverflow.com/questions/57979867/how-to-download-amazon-s3-files-on-to-local-machine-in-folder-using-python-and-b

    print(f's3 {bucket} {path}')
    s3 = boto3.resource('s3')
    response = s3.Bucket(bucket).objects.filter(Prefix=path)

    for item in response:
        filename = item.key.rsplit('/', 1)[-1]
        if filename.endswith('.csv'):
            print(f'{download_path}' + filename)
            s3.Object(bucket, item.key).download_file(f'{download_path}' + filename)

def s3_upload(s3_folder, upload_path):

    url = urlparse(s3_folder, allow_fragments=False)

    bucket = url.netloc
    path = url.path.lstrip('/')

    s3 = boto3.resource('s3')
    bucket = s3.Bucket(bucket)
 
    for subdir, dirs, files in os.walk(upload_path):
        for file in files:
            full_path = os.path.join(subdir, file)
            print(f'{subdir} {file}')
            with open(full_path, 'rb') as data:
                bucket.put_object(Key=path + file, Body=data)

def azblob_download(az_uri, download_path):
    # https://docs.microsoft.com/en-us/rest/api/storageservices/naming-and-referencing-containers--blobs--and-metadata#resource-uri-syntax
                    
    # Example: https://myaccount.blob.core.windows.net/mycontainer/myblob

    url = az_uri.replace('https://', '')

    # myaccount.blob.core.windows.net/mycontainer/myblob
    account_name = url[0: url.find('.')]
    first_slash = url.find('/') + 1
    second_slash = url.find('/', first_slash)
    container_name = url[first_slash: second_slash]
    path = url[second_slash: len(url.length)]
    print(f'az blob {account_name} {container_name} {path}')
    # https://stackoverflow.com/questions/42875787/download-all-blobs-files-locally-from-azure-container-using-python

    from azure.storage.blob import BlockBlobService

    block_blob_service = BlockBlobService(account_name=account_name, account_key=self.get_env_vars()['azure_storage_key'])
    generator = block_blob_service.list_blobs(container_name)

    for blob in generator:
        # Using `get_blob_to_bytes`
        b = service.get_blob_to_bytes(container_name, blob.name)
        fp = open(f'{download_path}{blob.name}', 'ab')
        fp.write(b.content)
        # Or using `get_blob_to_stream`
        # service.get_blob_to_stream(container_name, blob.name, fp)

    fp.flush()
    fp.close()