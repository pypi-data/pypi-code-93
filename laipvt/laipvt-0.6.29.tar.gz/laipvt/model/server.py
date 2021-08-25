from __future__ import absolute_import
from __future__ import unicode_literals
import subprocess
from laipvt.sysutil.util import ssh_obj, log
from laipvt.helper.errors import RuntimeErrors

class ServerModel():
    def __init__(self, server):
        self.server_obj = {}
        if type(server) == list:
            for s in server:
                self.server_obj[s.ipaddress] = ssh_obj(s.ipaddress, s.username, s.password, port=s.port)
        else:
            self.server_obj[server.ipaddress] = ssh_obj(server.ipaddress, server.username, server.password, port=server.port)

    def _send(self, cli, src, dest, ipaddr):
        try:
            cli.put(src, dest)
        except Exception as e:
            log.error(RuntimeErrors().SEND_FILE_ERROR.format(src, ipaddr, e))

    def _run(self, cli, cmd, ipaddr):
        try:
            cli.run_cmd(cmd)
        except Exception as e:
            log.error(RuntimeErrors().RUN_CMD_ERROR.format(ipaddr, cmd, e))


    def send_file(self, src, dest, ip=""):
        if ip:
            cli = self.server_obj[ip]
            self._send(cli, src, dest, ip)
        else:
            for ip in self.server_obj:
                self._send(self.server_obj[ip], src, dest, ip)

    def exec_cmd(self, cmd, ip=""):
        if ip:
            cli = self.server_obj[ip]
            self._run(cli, cmd, ip)
        else:
            for ip in self.server_obj:
                self._run(self.server_obj[ip], cmd, ip)

    def send_and_exec(self, src, dest, cmd, ip=""):
        if ip:
            cli = self.server_obj[ip]
            self._send(cli, src, dest, ip)
            self._run(cli, cmd, ip)
        else:
            for ip in self.server_obj:
                self._send(self.server_obj[ip], src, dest, ip)
                self._run(self.server_obj[ip], cmd, ip)

    def close(self):
        for ip in self.server_obj:
            self.server_obj[ip].close()

def runcmd(command, timeout=1000):
    ret = subprocess.run(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        encoding="utf-8", timeout=timeout
    )
    return ret.returncode, ret
