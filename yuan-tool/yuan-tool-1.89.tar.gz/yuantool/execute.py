import paramiko
import os
import sys
import logging
import psutil
import functools
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from .crypto import md5

UNIX: bool = os.name == 'posix'
SYS: str = sys.platform

#          os.name platform.system() sys.platform
# windows: nt      Windows           win32
# MacOS:   posix   Darwin            darwin
# Linux:   posix   Linux             linux


logger = logging.getLogger(__name__)


class ExecShellRemote:
    """
    执行远程linux shell命令
    """

    def __init__(self, hostname: str, port: int, username: str, password: str):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

    def create_remote_connection(self, info=False) -> bool:
        try:
            # 实例化SSHClient
            self.client = paramiko.SSHClient()
            # 自动添加策略，保存服务器的主机名和密钥信息
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostname=self.hostname, port=self.port, username=self.username, password=self.password)
            return True
        except Exception as e:
            logger.error(e, exc_info=info)
            return False

    def remote_exec(self, cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        return '\n'.join(stdout.readlines())


def ExecShell(cmdstring: str, shell=True):
    if SYS == 'linux':
        return ExecShellUnix(cmdstring, shell)
    elif SYS == 'darwin':
        return ExecShellMac(cmdstring, shell)
    elif SYS == 'win32':
        return ExecShellWindows(cmdstring, shell)


def ExecShellUnix(cmd: str, timeout=None, shell=True):
    """
    Linux平台下执行shell命令
    """
    a: str = ''
    e: str = ''

    try:
        rx: str = md5(cmd)
        succ_f = tempfile.SpooledTemporaryFile(
            max_size=4096,
            mode='wb+',
            suffix='_succ',
            prefix='btex_' + rx,
            dir='/dev/shm'
        )
        err_f = tempfile.SpooledTemporaryFile(
            max_size=4096,
            mode='wb+',
            suffix='_err',
            prefix='btex_' + rx,
            dir='/dev/shm'
        )
        sub = subprocess.Popen(
            cmd,
            close_fds=True,
            shell=shell,
            bufsize=128,
            stdout=succ_f,
            stderr=err_f
        )
        sub.wait(timeout=timeout)
        err_f.seek(0)
        succ_f.seek(0)
        a = succ_f.read()
        e = err_f.read()
        if not err_f.closed: err_f.close()
        if not succ_f.closed: succ_f.close()
        try:
            sub.kill()
        except OSError:
            pass
    except Exception as err:
        print(err)
    try:
        if isinstance(a, bytes): a = a.decode('utf-8')
        if isinstance(e, bytes): e = e.decode('utf-8')
    except Exception as err:
        print(err)
    return a, e


def ExecShellMac(cmd: str, shell=True):
    '''
    执行Shell命令（MacOS）

    :param cmdstring : str
    :param shell : (optional) The default is True.
    :returns  a,e
    '''
    a: str = ''
    e: str = ''

    try:
        sub = subprocess.Popen(
            cmd,
            close_fds=True,
            shell=shell,
            bufsize=-1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        a, e = sub.communicate()
        if not sub.stdout.closed: sub.stdout.close()
        if not sub.stderr.closed: sub.stderr.close()
        try:
            sub.kill()
        except OSError:
            pass
    except Exception as err:
        print(err)
    try:
        if isinstance(a, bytes): a = a.decode('utf-8')
        if isinstance(e, bytes): e = e.decode('utf-8')
    except Exception as err:
        print(err)
    return a, e


def ExecShellWindows(cmd: str, shell=True):
    '''
    执行Shell命令（MacOS）

    :param cmdstring : str
    :param shell : (optional) The default is True.
    :returns  a,e
    '''
    a: str = ''
    e: str = ''

    try:
        sub = subprocess.Popen(
            cmd,
            close_fds=False,
            shell=shell,
            bufsize=-1,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        a, e = sub.communicate()
        if not sub.stdout.closed: sub.stdout.close()
        if not sub.stderr.closed: sub.stderr.close()
        try:
            sub.kill()
        except OSError:
            pass
    except Exception as err:
        print(err)
    try:
        if isinstance(a, bytes): a = a.decode('utf-8')
        if isinstance(e, bytes): e = e.decode('utf-8')
    except Exception as err:
        print(err)
    return a, e


def local_exec(cmd):
    try:
        result = os.popen(cmd)
        return '\n'.join(result.readlines())
    except Exception as e:
        logger.error(e, exc_info=True)
        return False


def local_exec_by_subprocess(cmd, **kwargs):
    try:
        p = subprocess.Popen(cmd, bufsize=-1, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             close_fds=(SYS != "win32"), **kwargs)

        (output, error) = p.communicate()
    except Exception as e:
        logger.error(e, exc_info=True)
        return False


def perform(func, data, func_args=None, asynch=False, workers=None, progress=False, desc='Loading...'):
    """
    Wrapper arround executable and the data list object.
    Will execute the callable on each object of the list.
    Parameters:

    - `func`: callable stateless function. func is going to be called like `func(item, **func_args)` on all items in data.
    - `data`: if stays None, will perform the action on all rows, else it will perfom the action on the data list.
    - `func_args`: dict that will be passed by default to func in all calls.
    - `asynch`: execute the task asynchronously
    - `workers`: mandatory if asynch is true.
    - `progress`: to show progress bar with ETA (if tqdm installed).
    - `desc`: Message to print if progress=True
    Returns a list of returned results
    """
    if not callable(func):
        raise ValueError('func must be callable')
    # Setting the arguments on the function
    func = functools.partial(func, **(func_args if func_args is not None else {}))
    # The data returned by function
    returned = list()
    elements = data
    try:
        import tqdm
    except ImportError:
        progress = False
    tqdm_args = dict()
    # The message will appear on loading bar if progress is True
    if progress is True:
        tqdm_args = dict(desc=desc, total=len(elements))
    # Runs the callable on list on executor or by iterating
    if asynch:
        if isinstance(workers, int):
            if progress:
                returned = list(tqdm.tqdm(ThreadPoolExecutor(max_workers=workers).map(func, elements), **tqdm_args))
            else:
                returned = list(ThreadPoolExecutor(max_workers=workers).map(func, elements))
        else:
            raise AttributeError('When asynch == True : You must specify a integer value for workers')
    else:
        if progress:
            elements = tqdm.tqdm(elements, **tqdm_args)
        for index_or_item in elements:
            returned.append(func(index_or_item))
    return returned


def schedule_job(func, blocking=False, **kwargs):
    """
    :param func: 定时任务
    :param kwargs:
            trigger: 'interval' 时间间隔型任务 kwargs: seconds
                     'cron' 定时任务  kwargs: hour/minute
    :return:
    """

    if not blocking:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
    else:
        from apscheduler.schedulers.blocking import BlockingScheduler
        scheduler = BlockingScheduler()

    scheduler.add_job(func, **kwargs)
    scheduler.start()


def kill_child_process(pid):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        logger.info("kill child_process {}".format(child))
        child.kill()


def exit_gracefully(signum, frame):
    logger.info('Receive signal {} frame {}'.format(signum, frame))
    pid = os.getpid()
    kill_child_process(pid)
    parent = psutil.Process(pid)
    logger.info("kill self {}".format(parent))
    parent.kill()
