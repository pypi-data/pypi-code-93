import pickle

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload

import os
import io
import mimetypes


with open('token.pickle', 'rb') as token:
    credentials = pickle.load(token)

SERVICE = build("drive", "v3", credentials=credentials)

def load_file_list(folder_id:str, page_size=100) -> list:
    """入力されたフォルダーIDに保存されているファイルのIDと名前をdictで返します

    Args:
        folder_id (str): フォルダーID
        page_size (int): Max検索数
    
    Note:
        page_sizeの初期値は100に設定しています。
        指定のフォルダ内にファイルが100以上ある場合は、自分で調整してください。
    """
    query = f"'{folder_id}' in parents and trashed=false"

    result = SERVICE.files().list(
        pageSize=page_size, fields="nextPageToken, files(id, name)", q=query
    ).execute()

    items: list = result.get('files', [])

    return items

def download_file(file_id: str, save_file_name: str) -> None:
    """ファイルIDを指定して、そのファイルをダウンロードします。

    Args:
        file_id (str): ダウンロードしたいファイルのファイルID
        save_file_name (str): ローカルディレクトリに保存する際のファイル名
    
    Example:
        カレントディレクトリのDLフォルダに、sample.csvとして保存する場合
        >>> import os
        >>> cd = os.getcwd()
        >>> file_name = 'sample.csv'
        >>> save_file_name = os.path.join(cd, 'DL', file_name)

        >>> file_id = 'XXXXXXXXXXXXXXXXXXXX'
        >>> download_file(file_id, save_file_name)
        None

    """
    request = SERVICE.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    
    fh.seek(0)
    
    with open(save_file_name, 'wb') as f:
        f.write(fh.read())
        f.close()

def upload_file(folder_id: str, file_path:str) -> dict:
    """ローカルに保存されているファイルを、入力されたフォルダIDのフォルダにアップロードします

    Args:
        folder_id (str): アップロードしたいフォルダのフォルダーID
        file_path (str): アップロードしたいローカルファイルのファイルパス
    
    Note:
        file_pahはフルパスで入力した方が、安定します
    
    Return:
        upload_file (dict): アップロードされたファイルのファイルIDが格納されたdict
        {'id': 'XXXXXXXXXXXXX'}
    """
    mime = mimetypes.guess_type(f"{file_path}")[0]
    file_name = os.path.basename(file_path)

    file_metadata = {"name": file_name, "mimeType": mime, "parents": [folder_id] }
    media = MediaFileUpload(file_path, mimetype=mime, resumable=True)

    upload_file = SERVICE.files().create(body=file_metadata, media_body=media, fields='id').execute()

    return upload_file

def delete_file(file_id: str):
    """入力されたファイルID、フォルダIDのファイルを削除します

    Args:
        file_id (str): 削除したいファイルのファイルID
    """
    SERVICE.files().delete(fileId = file_id).execute()

def create_folder(folder_id: str, folder_name: str) -> dict:
    """入力されたフォルダIDに、入力されたフォルダ名でフォルダを作成し、作成したフォルダのIDを返します

    Args:
        folder_id (str): 作成したフォルダの格納先
        folder_name (str): 作成したいフォルダの名前
    
    Return:
        作成したフォルダのIDをdictで返します
        created_folder_id = {'id': 'XXXXXXXXXXXXXXXXXX'}
    """

    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [folder_id]
    }

    created_folder_id: dict = SERVICE.files().create(body=file_metadata, fields='id').execute()

    return created_folder_id