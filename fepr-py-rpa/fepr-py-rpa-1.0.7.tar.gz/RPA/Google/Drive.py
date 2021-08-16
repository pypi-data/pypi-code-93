import os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import mimetypes
from ..logger import logger


class DriveMetadata(object):
    def __init__(self, file_ids: list, file_titles: list):
        self.file_ids = file_ids
        self.file_titles = file_titles

    @property
    def drive_meta_dict(self) -> list:
        meta_dict: dict = {}
        meta_list: list = []
        for i in range(len(self.file_titles)):
            meta_dict['title'] = self.file_titles[i]
            meta_dict['id'] = self.file_ids[i]
            meta_list.append(meta_dict.copy())

        return meta_list


class Drive(object):
    def __init__(self):
        auth = GoogleAuth()
        auth.LocalWebserverAuth()
        self.drive = GoogleDrive(auth)

    def all_trash(self, drive_id: str):
        query = f"'{drive_id}' in parents and trashed=false"
        file_lists = self.drive.ListFile({'q': query}).GetList()

        logger.info({
            'action': 'all_trash',
            'status': 'running',
            'message': {
                'drive_id': drive_id
            }
        })

        for file_id in file_lists:
            f = self.drive.CreateFile({'id': file_id["id"]})

            logger.info({
                'action': 'all_trash',
                'status': 'running',
                'message': {
                    'file_name': f'{file_id["title"]} trashed'
                }
            })

            f.Trash()

        logger.info({
            'action': 'all_trash',
            'status': 'Success!',
        })

    def trash(self, file_id: str):
        logger.info({
            'action': 'trash',
            'status': 'Success!',
            'message': {
                    'file_id': file_id
                    }
        })

        f = self.drive.CreateFile({'id': file_id})
        f.Trash()
        logger.info({
            'action': 'trash',
            'status': 'Success!',
        })

    def upload(self, drive_id: str, file_path: str):
        mime = mimetypes.guess_type(f"{file_path}")[0]
        file_name = os.path.basename(file_path)
        file_set = self.drive.CreateFile({
            'title': file_name,
            'mimeType': mime,
            "parents": [{"id": drive_id}]
        })

        logger.info({
            'action': 'upload',
            'status': 'running',
            'message': {
                    'file_path': file_path,
                    'file_name': file_name,
                    'drive_id': drive_id
                    }
        })
        file_set.SetContentFile(f"{file_path}")
        file_set.Upload()

        logger.info({
            'action': 'upload',
            'status': 'Success!'
        })

    def download(self, drive_id: str, file_name: str, download_dir_path: str):
        query = f"'{drive_id}' in parents and trashed=false"
        file_id = self.drive.ListFile({'q': query}).GetList()
        try:
            for i in range(len(file_id)):
                if file_name == file_id[i]["title"]:
                    f = self.drive.CreateFile({'id': file_id[i]["id"]})
                    f.GetContentFile(os.path.join(
                        download_dir_path, file_id[i]["title"]))
                    logger.info({
                        'action': 'download',
                        'status': 'Success!',
                    })
                    break
                elif i == len(file_id)-1:
                    raise ValueError('指定したファイルは見つかりません')
        except Exception as e:
            logger.error({
                'action': 'download',
                'status': 'Failure!',
                'message': e
            })
            raise

    def load_files(self, drive_id: str) -> DriveMetadata.drive_meta_dict:
        query = f"'{drive_id}' in parents and trashed=false"
        file_list = self.drive.ListFile({'q': query}).GetList()

        file_titles = [file['title'] for file in file_list]
        file_ids = [file['id'] for file in file_list]

        meta = DriveMetadata(file_ids, file_titles)
        return meta.drive_meta_dict

    def create_folder(self, drive_id: str, folder_name: str) -> str:
        folder = self.drive.CreateFile({
            'title': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            "parents": [{"id": drive_id}]
        })
        folder.Upload()
        return folder['id']
