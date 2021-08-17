import os
import socket
import paramiko

from conn_diag.conn_diag.result import SSHResult
from conn_diag.conn_diag.constants import DEFAULT_SSH_TIMEOUT
from conn_diag.conn_diag.exceptions import SSHConnectionError


def local_connect(command):
    try:
        result = os.popen(cmd=command)
        return SSHResult(host='127.0.0.1', failed=False, unauthorized=False, unreachable=False, stdout=result, stderr=result)
    except Exception:
        return SSHResult(host='127.0.0.1', failed=True, unauthorized=False, unreachable=False, stdout=result, stderr=result)


def ssh_connect(host, command, ssh_username, ssh_password=None, ssh_key=None, ssh_timeout=DEFAULT_SSH_TIMEOUT):
    # Avoid ssh to subnet IP
    if '/' in host:
        return SSHResult(host=host, failed=True, stdout=None, stderr=None, unreachable=False, unauthorized=False, failed_msg='subnet not allowed')

    ssh = paramiko.SSHClient()
    try:
        ssh.set_missing_host_key_policy(policy=paramiko.AutoAddPolicy())
        if ssh_key:
            try:
                pkey = paramiko.RSAKey.from_private_key_file(filename=ssh_key)
            except Exception as e:
                raise SSHConnectionError('Private key is not valid: "{}"'.format(e))
            ssh.connect(hostname=host, port=22, username=ssh_username, pkey=pkey, timeout=ssh_timeout)
        elif ssh_password:
            ssh.connect(hostname=host, port=22, username=ssh_username, password=ssh_password, timeout=ssh_timeout)
        else:
            raise SSHConnectionError('You must specify ssh password or ssh key')

        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command=command)

        if ssh_stdout.channel.recv_exit_status() > 0:
            return SSHResult(host=host, failed=True, unreachable=False, unauthorized=False, stdout=ssh_stdout, stderr=ssh_stderr)
        return SSHResult(host=host, failed=False, unauthorized=False, unreachable=False, stdout=ssh_stdout, stderr=ssh_stderr)
    except paramiko.ssh_exception.AuthenticationException:
        return SSHResult(host=host, failed=False, stdout=None, stderr=None, unreachable=False, unauthorized=True)
    # TODO: what is NoValidConnectionsError?
    except paramiko.ssh_exception.NoValidConnectionsError:
        return SSHResult(host=host, failed=False, stdout=None, stderr=None, unreachable=True, unauthorized=False)
    except socket.timeout:
        return SSHResult(host=host, failed=False, stdout=None, stderr=None, unreachable=True, unauthorized=False)
    finally:
        ssh.close()
