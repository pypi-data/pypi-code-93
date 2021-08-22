from datetime import datetime
import os
import subprocess
import time


def invalid(path):
    try:
        os.stat(path)
        return not os.path.ismount(path)
    except Exception as e:
        return True


def refresh_if_needed(source_server, source, target, options):
    print(datetime.strftime(datetime.now(), "%y-%m-%d %H:%M:%S"))
    if not invalid(target):
        print("Still mounted")
        return
    unmount = subprocess.call(["fusermount", "-u", target])
    if unmount != 0:
        print("Failed unmount")
    mount_command = [
        "sshfs",
        source_server + ":" + source,
        target,
        "-o",
        options,
    ]
    mount = subprocess.call(mount_command)
    if mount != 0:
        print("Failed mount")


def autorefreshing_sshfs_utility(source_server, source, target, options):
    while True:
        time.sleep(1)
        try:
            refresh_if_needed(source_server, source, target, options)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(e)
            pass
