import requests
import picsellia.pxl_exceptions as exceptions
import json
import os
import sys

class Urls:

    def __init__(self, host, auth):
        self.host = host
        self.auth = auth
        self.upload_id = None
        self.project_token = None
        self.project_type = None

    def _get_presigned_url(self, method, object_name, bucket_model=False):
        to_send = {"method": method, "object_name": object_name, "bucket_model": bucket_model}
        if method == 'post':
            r = requests.post(self.host + 'generate_presigned_url', data=json.dumps(to_send), headers=self.auth)
        if method == 'get':
            r = requests.post(self.host + 'generate_presigned_url', data=json.dumps(to_send), headers=self.auth)
        if r.status_code != 200:
            raise ValueError("Errors.")
        return r.json()["url"]

    def _init_multipart(self, object_name):
        """Initialize the upload to saved Checkpoints or SavedModel
        Raises:
            NetworkError: If it impossible to initialize upload
            ResourceNotFoundError: If no saved_model saved"""

        try:
            to_send = {"object_name": object_name}
            r = requests.get(self.host + 'init_multipart_upload', data=json.dumps(to_send), headers=self.auth)
            if r.status_code != 200:
                print(r.text)
                return False
            self.upload_id = r.json()["upload_id"]

        except Exception:
            raise exceptions.NetworkError('Impossible to initialize upload')

    def _get_url_for_part(self, no_part, object_name):
        """Get a pre-signed url to upload a part of Checkpoints or SavedModel
        Raises:
            NetworkError: If it impossible to initialize upload

        """
        try:
            to_send = {
                "object_name": object_name,
                "upload_id": self.upload_id, 
                "part_no": no_part
            }
            r = requests.post(self.host + 'generate_post_part_url', data=json.dumps(to_send), headers=self.auth)
            if r.status_code != 200:
                raise exceptions.NetworkError(f"Impossible to get an url.. because :\n{r.text}")
            return r.json()["url"]
        except Exception:
            raise exceptions.NetworkError("Impossible to get an url..")

    def _upload_part(self, file_path, object_name):
        try:
            max_size = 5 * 1024 * 1024
            urls = []
            file_size = os.path.getsize(file_path)
            upload_by = int(file_size / max_size) + 1
            with open(file_path, 'rb') as f:
                for part in range(1, upload_by + 1):
                    signed_url = self._get_url_for_part(part, object_name)
                    urls.append(signed_url)
                parts = []
                for num, url in enumerate(urls):
                    part = num + 1
                    done = int(50 * num / len(urls))
                    try:
                        file_data = f.read(max_size)
                        res = requests.put(url, data=file_data)
                        if res.status_code != 200:
                            raise exceptions.NetworkError(f"Impossible to put part no {num + 1}\n because {res.text}")
                        etag = res.headers['ETag']
                        parts.append({'ETag': etag, 'PartNumber': part})
                        sys.stdout.write(f"\r{'=' * done}{' ' * (50 - done)}]")
                        sys.stdout.flush()
                    except Exception:
                        raise exceptions.NetworkError(f"Impossible to put part no {num+1}")
                return parts
        except Exception:
            raise exceptions.NetworkError("Impossible to upload file to Picsell.ia backend")

    def _complete_part_upload(self, parts, object_name, network_id):
        """
            Complete the upload a part of Checkpoints or SavedModel
            Raises:
                NetworkError: If it impossible to initialize upload
        """
        try:
            to_send = {
                "object_name": object_name, 
                "upload_id": self.upload_id, 
                "parts": parts, 
                "network_id": network_id, 
            }

            r = requests.post(self.host + 'complete_part_upload', data=json.dumps(to_send), headers=self.auth)
            if r.status_code != 201:
                exceptions.NetworkError(f"Impossible to get an url.. because :\n{r.text}")
            return True
        except Exception:
            raise exceptions.NetworkError("Impossible to get an url..")

    def _send_chunk_custom(self, chunk_annotations):
        to_send = {'format': 'custom', 'annotations': chunk_annotations, 'project_token': self.project_token, "project_type": self.project_type}

        try:
            r = requests.post(self.host + 'upload_annotations', data=json.dumps(to_send), headers=self.auth)
            if r.status_code == 400:
                raise exceptions.NetworkError(f"Impossible to upload annotations to Picsell.ia backend because \n {r.text}")
            print(f"{len(chunk_annotations['annotations'])} annotations uploaded")
        except Exception:
            raise exceptions.NetworkError("Impossible to upload annotations to Picsell.ia backend")

    def _send_chunk_picsell(self, chunk_annotations):
        to_send = {'format': 'picsellia', 'annotations': chunk_annotations, 'project_token': self.project_token, "project_type": self.project_type}

        try:
            r = requests.post(self.host + 'upload_annotations', data=json.dumps(to_send), headers=self.auth)
            if r.status_code == 400:
                raise exceptions.NetworkError(f"Impossible to upload annotations to Picsell.ia backend because \n {r.text}")
            print(f"{len(chunk_annotations['annotations'])} annotations uploaded")
        except Exception:
            raise exceptions.NetworkError("Impossible to upload annotations to Picsell.ia backend")

