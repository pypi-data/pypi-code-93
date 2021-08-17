import subprocess  # nosec
from dataclasses import dataclass
from typing import Optional


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    out: str


def run_command(cmd: str, timeout: int = 60) -> CommandResult:
    try:
        process = subprocess.run(cmd, timeout=timeout, capture_output=True, shell=True)  # nosec
        stdout = process.stdout.decode("utf-8")
        stderr = process.stderr.decode("utf-8")
        out = stdout + stderr
        return CommandResult(stdout=stdout, stderr=stderr, out=out)
    except subprocess.TimeoutExpired:
        return CommandResult(stdout="", stderr="timeout", out="timeout")


def run_ssh_command(host: str, cmd: str, ssh_key_path: Optional[str] = None, timeout=60) -> CommandResult:
    ssh_cmd = "ssh -o 'StrictHostKeyChecking=no' -o 'LogLevel=ERROR'"
    if ssh_key_path:
        ssh_cmd += f" -i {ssh_key_path} "
    ssh_cmd += f" {host} {cmd}"
    return run_command(ssh_cmd, timeout=timeout)
