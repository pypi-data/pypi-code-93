import os,time
import socket
import paramiko
from stat import S_ISDIR as isdir
import  copy



constMosResult = {'delay':'No Result','mos':'0.0','Speech Level Gain':'','Noise Level Gain':''}

class commondata():
    def __init__(self):
        self.mosResult = copy.deepcopy(constMosResult)
        self.HOST = '10.219.33.45'
        self.machost = '10.219.33.45' #'10.242.167.159'
        self.username = 'netease'
        self.password = 'Netease163'
        self.PORT = 2159
        self.sftpPort = 22
    @staticmethod
    def get_data():
        return {"type": "command",
        "module": "clientA",
        "method": "requestA",
        "samplerate":16000,
        "token": "",
        "job":None,
        "srcFile":'',
        "testFile":'',
        "result":{},
        "err":"No error"}

global_result = commondata()
def log_time():
    time_tup = time.localtime(time.time())
    # format_time = '%Y-%m-%d_%a_%H-%M-%S'
    format_time = '%Y-%m-%d-%H-%M-%S'

    cur_time = time.strftime(format_time, time_tup)
    return cur_time

def getip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        vqtip = s.getsockname()[0]
    finally:
        s.close()

    return vqtip


def exec_shell_command(cmd):
    ssh = paramiko.SSHClient()
    # 把要连接的机器添加到known_hosts文件中
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接服务器
    ssh.connect(hostname=serverIP, port=port, username=username, password=password, allow_agent=False,
                look_for_keys=False)
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)
    result = stdout.read()
    ssh.close()
    return result



def sftp_connect(username,password,host,port=22):
    client = None
    sftp = None
    try:
        client = paramiko.Transport((host,port))
    except Exception as error:
        print(error)
    else:
        try:
            client.connect(username=username, password=password)
        except Exception as error:
            print(error)
        else:
            sftp = paramiko.SFTPClient.from_transport(client)
    return client,sftp


def sftp_disconnect(client):
    try:
        client.close()
    except Exception as error:
        print(error)





def _check_local(local):
    if not os.path.exists(local):
        try:
            os.mkdir(local)
        except IOError as err:
            print(err)


def sftp_get(sftp, remote, local):
    # 检查远程文件是否存在
    try:
        result = sftp.stat(remote)
    except IOError as err:
        error = '[ERROR %s] %s: %s' % (err.errno, os.path.basename(os.path.normpath(remote)), err.strerror)
        print(error)
    else:
        # 判断远程文件是否为目录
        if isdir(result.st_mode):
            dirname = os.path.basename(os.path.normpath(remote))
            local = os.path.join(local, dirname)
            _check_local(local)
            for file in sftp.listdir(remote):
                sub_remote = os.path.join(remote, file)
                sub_remote = sub_remote.replace('\\', '/')
                sftp_get(sftp, sub_remote, local)
        else:
            # 拷贝文件
            if os.path.isdir(local):
                local = os.path.join(local, os.path.basename(remote))
            try:
                sftp.get(remote, local)
            except IOError as err:
                print(err)
            else:
                print('[get]', local, '<==', remote)


def sftp_put(sftp, local, remote):
    # 检查路径是否存在
    def _is_exists(path, function):
        path = path.replace('\\', '/')
        try:
            function(path)
        except Exception as error:
            return False
        else:
            return True

    # 拷贝文件
    def _copy(sftp, local, remote):
        # 判断remote是否是目录
        if _is_exists(remote, function=sftp.chdir):
            # 是，获取local路径中的最后一个文件名拼接到remote中
            filename = os.path.basename(os.path.normpath(local))
            remote = os.path.join(remote, filename).replace('\\', '/')
        # 如果local为目录
        if os.path.isdir(local):
            # 在远程创建相应的目录
            _is_exists(remote, function=sftp.mkdir)
            # 遍历local
            for file in os.listdir(local):
                # 取得file的全路径
                localfile = os.path.join(local, file).replace('\\', '/')
                # 深度递归_copy()
                _copy(sftp=sftp, local=localfile, remote=remote)
        # 如果local为文件
        if os.path.isfile(local):
            try:
                sftp.put(local, remote)
            except Exception as error:
                print(error)
                print('[put]', local, '==>', remote, 'FAILED')
            else:
                print('[put]', local, '==>', remote, 'SUCCESSED')

    # 检查local
    if not _is_exists(local, function=os.stat):
        print("'" + local + "': No such file or directory in local")
        return False
    # 检查remote的父目录
    remote_parent = os.path.dirname(os.path.normpath(remote))
    if not _is_exists(remote_parent, function=sftp.chdir):
        print("'" + remote + "': No such file or directory in remote")
        return False
    # 拷贝文件
    _copy(sftp=sftp, local=local, remote=remote)


def get_file_path(root_path,file_list,dir_list):
    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path,dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            #递归获取所有文件和目录的路径
            get_file_path(dir_file_path,file_list,dir_list)
        else:
            file_list.append(dir_file_path)