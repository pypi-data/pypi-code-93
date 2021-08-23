import os
import json

def get_sftp_path():
    '''
    Checks if SFTP config exists.
    '''
    cwd = os.getcwd()
    target_path = os.path.join(cwd, '.vsode/sftp.json')
    return target_path

def modify_sftp(name: str, remote: str, ip: int,
                user: str, port: int, key_path: str):
    sftp_path = get_sftp_path()
    new_config = {
        "name": name,
        "host": ip,
        "protocol": "sftp",
        "port": port,
        "username": user,
        "remotePath": remote,
        "privateKeyPath" : key_path,
        "uploadOnSave": true,
        "watcher": {
            "files": "*.{py,.sh,.txt}"
        },
        "ignore": [
            ".vscode",
            "*.png",
            "*.jpg",
            "*.npy",
            ".git/",
            "*.pt",
            "wandb/"
        ]
    }
    if not os.path.exists(sftp_path):
        json.write(new_config, key_path)


        # create sftp
    else:
        old_config = json.loads(sftp_path)
        # TODO: update values from new config
        config = {
            **new_config
        }