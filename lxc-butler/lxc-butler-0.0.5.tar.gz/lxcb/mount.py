import os
import lxc

import lxcb.info


def add_mount(name, host_path, dest_path):
    # check that the host path is a directory
    if not os.path.isdir(host_path):
        print(f'{host_path} is not a directory')
        return False

    container = lxc.Container(name)

    # check that the container exists
    if not container.defined:
        print(f'The container {name} does not exist')
        return False

    # get the container's rootfs
    rootfs = os.path.dirname(container.config_file_name) + '/rootfs'
    # get the absolute path of the host path
    host_path = os.path.realpath(host_path)
    # get the dest_path relative to the rootfs
    dest_path = os.path.join(f'home/{lxcb.info.username}', dest_path)

    # get the current mount paths
    mount_paths = container.get_config_item('lxc.mount.entry')

    # check if the mount path already exists
    if any(m.startswith(host_path + ' ') for m in mount_paths):
        print(f'{host_path} is already mounted in config')
        return False

    # stop the container first
    container.stop()

    # create the dest dir on the container
    dest_dir = os.path.join(rootfs, dest_path)
    if not os.path.isdir(dest_dir):
        try:
            os.makedirs(dest_dir)
        except OSError:
            print(f'Unable to create {dest_dir}')
            return False

    # add the new mount path
    container.append_config_item(
        'lxc.mount.entry',
        f'{host_path} {dest_path} none bind 0 0',
    )
    container.save_config()

    return True
