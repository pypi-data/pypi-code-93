import logging

import paramiko

from .package import Package


class PackageFetcher(object):
  LIST_PACKAGES_COMMAND = {
    "rpm": "rpm -qa",
    "dpkg": "dpkg-query --show --showformat='${binary:Package}\\t${Version}\\n'"
  }

  def get_packages(self, hostname, *, username=None, type="rpm"):
    logging.info(f"Fetching package from {username}@{hostname}...")
    with paramiko.SSHClient() as client:
      client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      client.connect(hostname, username=username)
      session = client.get_transport().open_session()
      paramiko.agent.AgentRequestHandler(session)
      session.exec_command(PackageFetcher.LIST_PACKAGES_COMMAND[type])
      stdin = session.makefile_stdin("wb", -1)
      stdin.close()
      stdout = session.makefile("r", -1)
      stderr = session.makefile_stderr("r", -1)
      out_lines = stdout.readlines()
      err_lines = stderr.readlines()
      exit_status = session.recv_exit_status()
      if exit_status != 0:
        print(err_lines)
        raise ValueError(
            f"Querying packages from {hostname} failed with exit status {exit_status}")
      return [Package.parse(line.strip(), type=type) for line in out_lines]
