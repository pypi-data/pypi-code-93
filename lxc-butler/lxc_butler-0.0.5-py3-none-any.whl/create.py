import os
import time
import shlex
import lxc
import subprocess
import shutil

from ipaddress import IPv4Address

import lxcb.info


# returns the next available IP address
def _next_ip():
    ips = []

    for container in lxc.list_containers(as_object=True):
        # get the ip as set in the config
        ip = container.get_config_item('lxc.net.0.ipv4.address')

        if ip:
            ips.append(IPv4Address(ip.split('/')[0]))

    if not ips:
        # return a default first address
        return IPv4Address('10.0.3.2')

    # returns the ip address just after the max current address
    return max(ips) + 1


# create a new container
def create(name, distro, release, arch, ssh_config):
    container = lxc.Container(name)

    # check if the container already exists
    if container.defined:
        print(f'A container with the name "{name}" is already defined')
        return False

    # find the next available IP address
    ip = _next_ip()

    # update the pgp keyserver, since the one currently used by the download
    # template doesn't work anymore
    os.environ['DOWNLOAD_KEYSERVER'] = 'keys.openpgp.org'

    # create the container
    container.create('download', 0, {
        'dist': distro,
        'release': release,
        'arch': arch,
    })

    # set the container's ip address
    container.append_config_item('lxc.net.0.ipv4.address', str(ip))
    container.save_config()

    # start the container
    container.start()
    container.wait('RUNNING', 3)

    # wait for network connectivity
    print('Waiting for network connectivity')
    time.sleep(15)

    def run_cmd(cmd):
        container.attach_wait(lxc.attach_run_command, shlex.split(cmd))

    username = lxcb.info.username

    # update the container's repos
    run_cmd('apt update')
    # update the container's packages
    run_cmd('apt upgrade -y')
    # install an ssh server, sudo and bash-completion
    run_cmd('apt install -y openssh-server sudo bash-completion')
    # set the timezone
    run_cmd(f'ln -fs /usr/share/zoneinfo/{lxcb.info.timezone} /etc/localtime')
    # create the default user
    run_cmd(f'/usr/sbin/useradd -mG sudo -s /bin/bash {username}')

    # set the default user's password
    def set_password():
        subprocess.run(['/usr/bin/passwd', username],
                       input=f'{username}\n{username}\n'.encode())

    container.attach_wait(set_password)

    # read this machine's public ssh key
    with open(os.path.join(lxcb.info.home, '.ssh/id_rsa.pub'), 'r') as f:
        public_key = f.read()

    # add the host's ssh key to the container
    def add_key():
        # home directory of default user on container - not using expanduser
        # (gave some issues with some setups)
        container_home = f'/home/{username}'
        # ssh dir
        ssh_dir = os.path.join(container_home, '.ssh')
        # create the ssh dir
        if not os.path.isdir(ssh_dir):
            os.makedirs(ssh_dir)
        # add the key
        authorized_keys = os.path.join(ssh_dir, 'authorized_keys')
        with open(authorized_keys, 'w') as f:
            f.write(public_key)
        # make sure the user owns the ssh dir and authorized keys file
        # using direct id here because for some reason on some setups python
        # doesn't correctly read the passwd entries
        shutil.chown(ssh_dir, 1000, 1000)
        shutil.chown(authorized_keys, 1000, 1000)

    container.attach_wait(add_key)

    # add the container's ip address to the host's ssh config
    with open(ssh_config, 'a') as f:
        f.write(f'\nHost {name}\n  Hostname {ip}\n')

    return True
