"""Upload file on GoogleDrive."""
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


def authorization(secrets: str, credintials: str) -> GoogleDrive:
    """
    Start authorization on Gdrive.

    Parameters
    ----------
    secrets
        path to client secrets json
    credintials
        path to file with config for autorization on GDrive

    Returns
    -------
        googledrive object
    """
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = secrets
    gauth = GoogleAuth()
    gauth.LoadCredentialsFile(credintials)
    drive = GoogleDrive(gauth)
    return drive


def get_folder_data(drive: GoogleDrive, folder_id_path: str) -> list:
    """
    Return all files paths and id from user's GDrive.

    Parameters
    ----------
    drive
        GoogleDrive obj
    folder_id_path
        path to file with folder's id

    Returns
    -------
        list of file's names
    """
    with open(folder_id_path) as folder_id_file:
        folder_id = folder_id_file.read()
    file_list = drive.ListFile(
        {'q': "'" + folder_id.replace('\n', '') + "' in parents and trashed=false"}).GetList()
    return file_list


def upload(path: str, drive: GoogleDrive, folder_id_path: str):
    """
    Upload file on GoogleDrive using credentials.

    Parameters
    ----------
    path
        path to file to upload
    folder_id_path
        path to file with folder's id

    """
    with open(folder_id_path) as folder_id_file:
        folder_id = folder_id_file.read()
    with open(path, "r") as file_obj:
        file_name = os.path.basename(file_obj.name)
        file_drive = drive.CreateFile({
            'title': file_name,
            "parents": [{"id": folder_id.replace('\n', ''), "kind": "drive#childList"}]
            })
        file_drive.SetContentString(file_obj.read())
        file_drive.Upload()


def create_credentials(secrets: str, new_credintials: str):
    """
    Initialize reauthorization and create creds if they contain error.

    Parameters
    ----------
    secrets
        path to client secrets json
    new_credintials
        path to save or refresh credintials
    """
    GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = secrets
    gauth = GoogleAuth()
    # Try to load this file's data
    gauth.LoadCredentialsFile(new_credintials)
    if gauth.credentials is None:
        # if it is doesn't exist - start browser inicialization
        gauth.LocalWebserverAuth()
    elif gauth.access_token_expired:
        # if token is bad - refresh it
        gauth.Refresh()
    else:
        # if it's all right - trying to authorise
        gauth.Authorize()
    # Save or resave creds into choosen file's path
    gauth.SaveCredentialsFile(new_credintials)


def get_files_id(drive: GoogleDrive):
    """
    Show folders and files id's on GDrive and places Users Drive chained.

    Parameters
    ----------
    drive
        GoogleDrive obj
    """
    folder_list = drive.ListFile({'q': "trashed=false"}).GetList()
    for folder in folder_list:
        print('folder title: %s, id: %s' % (folder['title'], folder['id']))


def delete_file_by_name(file_name: str, drive: GoogleDrive, folder_id_path: str):
    """
    Delete file by name.

    Except: few files with same name.

    Parameters
    ----------
    file_name
        name of file to delete
    drive
        GoogleDrive obj
    folder_id_path
        path to file with folder's id
    """
    files = get_folder_data(drive, folder_id_path)
    objs = []
    for obj in files:
        if obj['title'] == file_name:
            objs.append(obj)
    if len(objs) == 1:
        file1 = drive.CreateFile({'id': objs[0]['id']})
        file1.Delete()
    elif len(objs) == 0:
        print("There are no files with name:", file_name)
    else:
        print("There ara several files with name:", file_name)
