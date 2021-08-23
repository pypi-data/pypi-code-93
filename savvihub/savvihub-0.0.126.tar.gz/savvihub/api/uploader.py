import os

from savvihub.api.file_object import UploadableS3MultipartFileObject
from savvihub.common.utils import calculate_crc32c


def default_hooks():
    def fn(resp, **kwargs):
        resp.raise_for_status()
    return {
        'response': fn,
    }


class Uploader:
    @classmethod
    def get_files_to_upload(cls, local_base_path, hashmap=None):
        local_base_path = local_base_path.rstrip('/')
        results = []
        for root, dirs, files in os.walk(local_base_path):
            for name in files:
                name = os.path.join(root, name)
                name = name[len(local_base_path) + 1:] if name.startswith(local_base_path) else name
                if hashmap and hashmap[name] == calculate_crc32c(os.path.join(local_base_path, name)):
                    continue
                results.append(name)
        return results

    @classmethod
    def get_hashmap(cls, local_base_path):
        files = cls.get_files_to_upload(local_base_path)
        hashmap = dict()
        for file in files:
            path = os.path.join(local_base_path, file)
            hashmap[file] = calculate_crc32c(path)
        return hashmap

    @classmethod
    def upload(cls, client, local_path, volume_id, remote_path, progressable=None):
        file_object = client.volume_file_create(volume_id, remote_path, is_dir=False)

        mpu = UploadableS3MultipartFileObject(
            file_object.upload_url.federation_token.bucket,
            file_object.upload_url.federation_token.key,
            local_path,
            file_object.upload_url.federation_token.token,
        )
        mpu.abort_all()
        mpu_id = mpu.create()
        parts = mpu.upload(mpu_id)
        mpu.complete(mpu_id, parts)
        resp = client.volume_file_uploaded(volume_id, remote_path)
        return resp

    @classmethod
    def bulk_upload(cls, client, local_base_path, local_file_paths, volume_id, remote_base_path, *, progressable=None):
        # TODO: parallel upload
        if len(local_file_paths) <= 0:
            return

        file_objects = []
        for local_file_path in local_file_paths:
            file_objects.append(client.volume_file_create(
                volume_id,
                os.path.join(remote_base_path, local_file_path),
                is_dir=False,
                # hooks=default_hooks()
            ))

        for i, file_object in enumerate(file_objects):
            mpu = UploadableS3MultipartFileObject(
                file_object.upload_url.federation_token.bucket,
                file_object.upload_url.federation_token.key,
                os.path.join(local_base_path, local_file_paths[i]),
                file_object.upload_url.federation_token.token,
            )
            mpu.abort_all()
            mpu_id = mpu.create()
            parts = mpu.upload(mpu_id)
            mpu.complete(mpu_id, parts)

        for local_file_path in local_file_paths:
            client.volume_file_uploaded(
                volume_id,
                os.path.join(remote_base_path, local_file_path),
                # hooks=default_hooks(),
            )

        return file_objects
