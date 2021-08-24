import pkg_resources
import paramiko  # 用于调用scp命令
from scp import SCPClient

print('hello')
sop_name = "data/com.syberos.sgt-1.0.2.sop"
if pkg_resources.resource_exists(__name__, sop_name):
    sop = pkg_resources.resource_stream(__name__, sop_name)
    f = open("./base.sop", "wb")
    f.write(sop.read())
    f.close()

    host = "192.168.100.100"
    port = 22
    username = "developer"
    password = "system"

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(host, port, username, password)
    scp_client = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)
    scp_client.put("./base.sop", "/tmp/")

    print("push sgt to device and launch sgt")
    ssh_client.exec_command("ins-tool -iu /tmp/base.sop && dbus-send --system --print-reply --dest=com.syberos.compositor /com/syberos/compositor com.syberos.compositor.CompositorInterface.emitLaunchApp string:com.syberos.sgt string:SGT")

    ssh_client.close()
