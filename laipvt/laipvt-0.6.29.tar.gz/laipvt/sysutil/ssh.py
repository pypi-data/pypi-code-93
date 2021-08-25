from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys
import paramiko
import tarfile
import time
import re
import socket
import subprocess
import shutil
from laipvt.helper.exception import SSHAuthFailed, SSHAuthInfoMissed, SSHConnectFailed, SSHPortFailed, \
    SSHPortOrIpIllegal
from laipvt.helper.errors import FileTypeErrors
from paramiko.ssh_exception import AuthenticationException, NoValidConnectionsError


def monkey_sudo(password, cmd):
    cmd = "echo '{}' | sudo -S {}".format(password, cmd)
    return cmd


def to_str(bytes_or_str):
    """
    把byte类型转换为str
    :param bytes_or_str:
    :return:
    """
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value


class SSHConnect(object):
    """
        封装paramiko类，实现ssh执行命令、上传下载文件
    """

    def __init__(self, hostip, username, ssh_key="", password="", port=22, timeout=5, encoding="utf8", **kwargs):
        """
        :param hostip: 主机IP
        :param username: 主机用户
        :param password:  主机密码
        :param port: 主机端口，默认22，可传
        """
        self.hostip = hostip
        self.port = port
        self.username = username.strip()
        self.password = password.strip()
        self.ssh_key = ssh_key
        self.timeout = timeout
        self.encoding = encoding
        ips = []
        try:
            addr_info = socket.getaddrinfo(socket.gethostname(), None)
            for addr in addr_info:
                ips.append(addr[4][0])
        except socket.gaierror:
            pass

        self.is_local = True if self.hostip in ips else False

        # 创建一个ssh对象，用于ssh登录以及执行操作
        self.obj = paramiko.SSHClient()
        # 如果第一次连接陌生的IP,自动选择yes确认连接
        self.obj.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # 连接服务器
        if not self.is_local:
            try:
                if self.password:
                    self.obj.connect(hostname=self.hostip, port=self.port, username=self.username,
                                     password=self.password,
                                     timeout=self.timeout)
                    self.objsftp = self.obj.open_sftp()
                    self.chan = self.obj.invoke_shell()
                    self.chan.settimeout(9000)

                elif self.ssh_key:
                    self.pkey = paramiko.RSAKey.from_private_key_file(self.ssh_key)
                    self.obj.connect(hostname=self.hostip, port=self.port, username=self.username, pkey=self.pkey,
                                     timeout=self.timeout)
                    self.objsftp = self.obj.open_sftp()
                    self.chan = self.obj.invoke_shell()
                    self.chan.settimeout(9000)
                else:
                    raise SSHAuthInfoMissed()
            except AuthenticationException:
                raise SSHAuthFailed()
            except NoValidConnectionsError:
                raise SSHPortFailed()
            except socket.timeout:
                raise SSHConnectFailed()
            except socket.gaierror:
                raise SSHPortOrIpIllegal()

    def run_cmd(self, cmd):
        """
        执行命令
        :param cmd: 需要执行的命令
        :return: 执行结果
        """
        cmd = monkey_sudo(self.password, cmd)
        if self.is_local:
            code, res = subprocess.getstatusoutput(cmd)
            err = res
        else:
            stdin, stdout, stderr = self.obj.exec_command(cmd, get_pty=True)
            code, res, err = stdout.channel.recv_exit_status(), stdout.read(), stderr.read()
            r = re.compile("\[sudo.*: ")
            res = r.sub("", to_str(res))
        # result = res if res else err
        res = {
            "code": code,
            "stdout": to_str(res),
            "stderr": to_str(err)
        }
        return res

    def run_cmdlist(self, cmdlist):
        self.resultList = []
        for cmd in cmdlist:
            # stdin, stdout, stderr = self.obj.exec_command(cmd)
            # self.resultList.append(stdout.read())
            res = self.run_cmd(cmd)
            self.resultList.append(res)
        return self.resultList

    def get(self, remotepath, localpath):
        """
        从远程服务器获取文件到本地
        """
        if self.is_local:
            localpath_dir = os.path.dirname(localpath)
            if not os.path.exists(localpath_dir):
                os.makedirs(localpath_dir)
            try:
                shutil.copy(remotepath, localpath)
            except IOError as e:
                print("Unable to copy file. %s" % e)
                exit(2)
            except:
                print("Unexpected error:", sys.exc_info())
                exit(2)
        else:
            self.objsftp.get(remotepath, localpath)

    def _file_translate(self, tmp_path, remote_path):
        # 去掉.tmp后缀，获取文件路径
        # ok_tmp_path = os.path.splitext(tmp_path)[0]
        result = self.run_cmd("mv {} {}".format(tmp_path, remote_path))
        result = self.run_cmd("chown root.root -R {}".format(remote_path))
        return result

    def put(self, localpath, remotepath, ignore=''):
        """
        从本地推送到远程服务器
        如果本地是目录，远程也会是目录
        如果本地是文件，远程也会是文件
        """
        # 判断本地要传的是文件还是目录，如果是文件直接传即可，目录需要打包
        if self.is_local:
            if os.path.isdir(localpath):
                try:
                    shutil.copytree(localpath, remotepath)
                except FileExistsError:
                    shutil.rmtree(remotepath, ignore_errors=True)
                    shutil.copytree(localpath, remotepath)
            else:
                try:
                    shutil.copy(localpath, remotepath)
                except FileNotFoundError:
                    os.makedirs(os.path.dirname(remotepath))
                    shutil.copy(localpath, remotepath)
                except shutil.SameFileError:
                    pass

        else:
            try:
                # 远程上传目录逻辑
                if os.path.isdir(localpath):
                    # 去掉path末尾斜杠
                    if localpath[-1] == '/':
                        localpath = localpath[0:-1]

                    # 打包tar文件，临时压缩文件，传输完成会删掉
                    # tar包名称
                    tar_name = "{}-{}.tar.gz".format(localpath.split("/")[-1], int(time.time()))
                    # 去掉远程最后一层目录,获取上层目录(创建目录)，因为后续还需要解压
                    top_remote_path = os.path.dirname(remotepath)
                    # 检查是否存在上层目录，不存在即创建
                    try:
                        self.objsftp.stat(top_remote_path)
                    except IOError:
                        result = self.run_cmd("mkdir -pv {}".format(top_remote_path))
                    # tar包路径
                    remote_tarfile_path = os.path.join(top_remote_path, tar_name)
                    # 把目录归档压缩成tar包
                    with tarfile.open(tar_name, "w:gz") as tar:
                        def filter_func(tarinfo):
                            if tarinfo.name == os.path.join(os.path.basename(localpath),ignore):
                                return None
                            else:
                                return tarinfo
                        tar.add(localpath, arcname=os.path.basename(localpath), filter=filter_func)
                    # 定义远程临时path（先放tmp中）
                    remote_tarfile_path_tmp = os.path.join("/tmp", "{}.tmp".format(tar_name))
                    self.objsftp.put(tar_name, remote_tarfile_path_tmp)
                    # 移动到正确的远程目录
                    # self._file_translate(
                    #     tmp_path=remote_tarfile_path_tmp, remote_path=top_remote_path
                    # )
                    # 远端进行解压
                    tar_command = "tar -zxf {} -C {}".format(remote_tarfile_path_tmp, top_remote_path)
                    result = self.run_cmd(tar_command)
                    if result["code"] != 0:
                        raise Exception(result)
                    # 删除本地临时tar文件
                    os.remove(tar_name)
                    # 删除远端临时tar文件
                    result = self.run_cmd("rm -f {}".format(remote_tarfile_path_tmp))
                    if result["code"] != 0:
                        raise Exception(to_str(result))

                elif os.path.isfile(localpath):
                    remote_dir_name = os.path.dirname(remotepath)
                    try:
                        self.objsftp.stat(remote_dir_name)
                    except IOError:
                        result = self.run_cmd("mkdir -pv {}".format(remote_dir_name))
                    # 定义远程临时path（先放tmp中）
                    file_name = "{}.tmp".format(os.path.basename(remotepath))
                    remote_path_tmp = os.path.join("/tmp", file_name)
                    self.objsftp.put(localpath, remote_path_tmp)
                    self._file_translate(
                        tmp_path=remote_path_tmp, remote_path=remotepath
                    )
                else:
                    print(FileTypeErrors().WRONG_FILE_TYPE)
            except Exception as e:
                raise Exception(e)

    def close(self):
        if not self.is_local:
            self.objsftp.close()
            self.obj.close()
        else:
            pass


if __name__ == '__main__':
    pass
