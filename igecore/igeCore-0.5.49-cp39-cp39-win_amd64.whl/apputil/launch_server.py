"""
launch_server.py

access igeLauncher apprication server
"""

import requests
import json
import hashlib
import os.path
import glob

#LAUNCH_SERVER_URL = 'http://127.0.0.1:8080'
LAUNCH_SERVER_URL = 'https://igelauncher.appspot.com'

def mkdir(dir,name):
    """
    Make a directory on the server

    :param dir:  parent directory name
    :param name: directory to create
    :return: 0 if success , not 0 if error
    """
    url = LAUNCH_SERVER_URL + '/mkdir'
    param = {'directory':dir,'name':name}
    try:
        response = requests.post(url, param)
    except:
        print('mkdir ; network error')
        return -1

    if response.status_code != 200:
        print('mkdir ; network error')
        if response.text is not None:
            print(response.text)
        return -1
    return 0

def ls(dir):
    """
    Lists directory contents of files and directories on the server

    :param dir: directory path
    :return: files, err
              files : {filename : {type:filetype, hash:hashvalue, sizse:filesize}}
               err: not 0 if error occurred
    """
    url = LAUNCH_SERVER_URL + '/ls'
    param = {'directory': dir}
    try:
        response = requests.post(url, param)
    except:
        return None, -1
    if response.status_code == 200:
        list = json.loads(response.text)
        return list,0
    else:
        print('Network error! Status Code: {:d}'.format(response.status_code))
        if response.text is not None:
            print(response.text)
    return None, -1

def download_files(src,dst):
    """
    Download all files in the specified directory on the server

    :param src: server directory path
    :param dst: local direcgtory path to save files
    :return: not 0 if error occurred
    """
    list,err = ls(src)
    if list is None: return err

    url = LAUNCH_SERVER_URL+'/download_request'

    for key, val in list.items():
        localHash = ""
        path = dst+'/'+key
        if os.path.exists(path):
            with open(path, 'rb') as f:
                fileDataBinary = f.read()
                if len(fileDataBinary) != 0:
                    hash = hashlib.md5()
                    hash.update(fileDataBinary)
                    localHash = hash.hexdigest()

        if localHash != val['hash']:
            param = {'directory':src,'file':key}

            try:
                response = requests.post(url, param)
                dlurl = response.text
                response = requests.get(dlurl)
            except:
                print('download {} was failed'.format(key))
                return -1

            if response.status_code == 200:
                with open(path, 'wb') as f:
                    f.write(response.content)
                print('downloaded {}'.format(key))
            else:
                print('Network error! Status Code: {:d}'.format(response.status_code))
                if response.text is not None:
                    print(response.text)
        else:
            print('download {} was skipped because no change'.format(key))
    return 0

def upload_files(src,dst):
    url = LAUNCH_SERVER_URL + '/ls'
    param = {'directory': dst}
    response = requests.post(url, param)

    serverFiles = {}
    if response.status_code == 200:
        serverFiles = json.loads(response.text)

    localFiles = []
    list = glob.glob(os.path.join(src, '*'))
    for f in list:
        if os.path.isfile(f):
            localFiles.append(f)
    for path in localFiles:
        fileDataBinary = ''
        with open(path, 'rb') as f:
            fileDataBinary = f.read()

        filesize = len(fileDataBinary)
        if filesize == 0: continue

        hash = hashlib.md5()
        hash.update(fileDataBinary)
        hashcode = hash.hexdigest()

        f = os.path.basename(path)
        if f not in serverFiles or serverFiles[f]['hash'] != hashcode:

            try:
                if filesize > 32*1024*1024:
                    url = LAUNCH_SERVER_URL + '/upload_start'
                    param = {'directory': dst, 'filename': os.path.basename(path), 'filesize':filesize, 'hash':hashcode}
                    response = requests.post(url, param)
                    url = response.text
                    response = requests.post(url, data=fileDataBinary)
                    url = LAUNCH_SERVER_URL + '/upload_finish'
                    response = requests.post(url, param)
                else:
                    url = LAUNCH_SERVER_URL + '/upload'
                    XLSX_MIMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    files = {'file': (f, fileDataBinary, XLSX_MIMETYPE)}
                    param = {'directory': dst, 'hash': hashcode}
                    response = requests.post(url, param, files=files)
            except:
                print('upload {} was failed'.format(f))
                return -1

            if response.status_code == 200:
                print(path + " uploaded.")
            else:
                print('Network error! Status Code {:d}\n'.format(response.status_code))
                if response.text is not None:
                    print(response.text)
        else:
            print(path + " is not changed.")

    return 0

def makeProjectDir(user, app, version, platform):
    root = '/'
    if mkdir(root, user) == 0:
        root += user
        if mkdir(root, app) == 0:
            root += '/'
            root += app
            if mkdir(root, version) == 0:
                root += '/'
                root += version
                if mkdir(root, platform)==0:
                    return True
    return False
