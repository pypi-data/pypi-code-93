import io
import os.path

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from . import auth

class Transfer:
    def upload_file(self, file_path, dest_folder = None):
        creds = auth.Auth().verify_token()

        if creds:
            service = build('drive', 'v3', credentials=creds)

            folder_id = None
            file_metadata = None
            file_name = os.path.basename(file_path)

            if dest_folder:
                folder_metadata = {
                    'name': dest_folder,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder_result = service.files().create(body=folder_metadata, fields="id").execute()
                folder_id = folder_result.get("id")

                file_metadata = {
                    'name': file_name,
                    "parents": [folder_id]
                }
            else:
                file_metadata = {
                    'name': file_name
                }                

            # upload file
            media = MediaFileUpload(file_path, resumable=True)
            file_result = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print('%s(%s) is uploaded.' % (file_name, file_result))

        else:
            print('verification failed. please login.')

    def download_file(self, file_id):
        creds = auth.Auth().verify_token()

        if creds:
            service = build('drive', 'v3', credentials=creds)

            # Call the Drive v3 API
            result = service.files().get(fileId=file_id).execute()
            file_name = result.get('name')

            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(file_name, 'wb')

            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print('download %d%%.' % int(status.progress() * 100))
        else:
            print('verification failed. please login.')