import subprocess
import sys
import os
import time

import fire
import psutil
import v2ray_runtime
import caddy_runtime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
BASE_DIR = BASE_DIR.replace('\\', '/')


def GetCurrentOS():
    temp = sys.platform
    if temp == 'win32':
        return 'Windows'
    if temp == 'cygwin':
        return 'Cygwin'
    if temp == 'darwin':
        return 'Mac'
    return 'Linux'


def DoCMD(cmd, is_wait=True, cwd=None):
    print('\n\n==', cmd, '\n')
    if is_wait:
        subprocess.Popen(cmd, shell=True, cwd=cwd).wait()
    else:
        subprocess.Popen(cmd, shell=True, cwd=cwd)


def Log(msg):
    print(msg)


def IsProcessExist(name):
    pids = psutil.pids()
    for pid in pids:
        try:
            p = psutil.Process(pid)
            temp = p.name()
            if name == temp:
                return p
        except Exception as e:
            pass
    # Log("process '%s' is not exist." % (name))
    return False


class UIFClient(object):
    def Run(self,
            domain,
            server_address=None,
            use_cloudfare=False,
            with_free_port=True,
            is_nohup=False):

        ###########
        #  check  #
        ###########
        if use_cloudfare is True and domain is None:
            raise ValueError('Need domain to enable cloudfare.')

        if domain is None:
            self.domain = 'localhost'
        else:
            self.domain = domain

        if server_address is None:
            self.server_address = 'https://uifv2ray.xyz'
        else:
            self.server_address = server_address

        if is_nohup is False:
            is_nohup = ''
        else:
            is_nohup = 'nohup '

        is_v2ray_running = IsProcessExist(v2ray_runtime.V2RAY_RUNTIME_NAME)
        is_caddy_running = IsProcessExist(caddy_runtime.CADDY_RUNTIME_NAME)

        if is_v2ray_running:
            Log('v2ray_running')
            is_v2ray_running.kill()
        if is_caddy_running:
            Log('caddy_running')
            is_caddy_running.kill()

        DoCMD('fuser -k -n tcp 80')  # for linux

        if with_free_port is False:
            caddy_template_file_path = BASE_DIR + '/caddy_config/tls_ws.txt'
        else:
            caddy_template_file_path = BASE_DIR + '/caddy_config/tls_ws_with_free.txt'

        with open(caddy_template_file_path, 'r+') as f:
            content = f.read()
            content = content.replace('{domain}', self.domain)
            print(content)

        caddy_config_file_path = BASE_DIR + '/caddy_config/using.caddyfile'
        with open(caddy_config_file_path, 'w+') as f:
            f.write(content)

        v2ray_config_file_path = BASE_DIR + '/v2ray_config/default.json'

        #########
        #  run  #
        #########
        # run v2ray first
        DoCMD('%s %s -config "%s"' %
              (is_nohup, v2ray_runtime.V2RAY_RUNTIME_PATH,
               v2ray_config_file_path),
              cwd=v2ray_runtime.V2RAY_RUNTIME_DIR,
              is_wait=False)

        time.sleep(5)

        DoCMD('%s %s run -config "%s" -adapter caddyfile' %
              (is_nohup, caddy_runtime.CADDY_RUNTIME_PATH,
               caddy_config_file_path),
              cwd=caddy_runtime.CADDY_RUNTIME_DIR,
              is_wait=False)

        time.sleep(5)

        SERVER_PATH = './ctrl/ctrl.py'
        if GetCurrentOS() == "Linux":
            CTRL_PATH = './ctrl/linux_x64.exe'
        else:
            CTRL_PATH = './ctrl/windows_x64.exe'

        DoCMD('%s %s' % (is_nohup, CTRL_PATH), cwd=BASE_DIR, is_wait=False)

        client_address = 'https://' + self.domain
        client_address_go = client_address + '/handle'
        DoCMD(
            '%s python3 %s --remote_address "%s" --client_address "%s" --client_address_go "%s"'
            % (is_nohup, SERVER_PATH, self.server_address, client_address,
               client_address_go),
            cwd=BASE_DIR,
            is_wait=False)

    def Test(self):
        with_free_port = True
        if with_free_port is False:
            caddy_template_file_path = BASE_DIR + '/caddy_config/tls_ws.txt'
        else:
            caddy_template_file_path = BASE_DIR + '/caddy_config/tls_ws_with_free.txt'
        print(caddy_template_file_path)

        with open(caddy_template_file_path, 'r+') as f:
            content = f.read()
            print(content)

    def Stop(self):
        pass

    def Restart(self):
        if use_cloudfare is False and self.domain is None:
            raise ValueError('Need domain to enable cloudfare.')


def Main():
    if GetCurrentOS() == 'Linux':
        cmd = "sudo chmod -R 750 " + BASE_DIR
        DoCMD(cmd)
        cmd = "sudo chmod -R 750 " + caddy_runtime.CADDY_RUNTIME_DIR
        DoCMD(cmd)
        cmd = "sudo chmod -R 750 " + v2ray_runtime.V2RAY_RUNTIME_DIR
        DoCMD(cmd)
    fire.Fire(UIFClient)


if __name__ == '__main__':
    Main()
