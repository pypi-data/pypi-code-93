import datetime
import hashlib
import os
import subprocess
import sys
from distutils.sysconfig import get_python_lib

import PyInquirer
import click
import daemon.daemon as ppd
import psutil

from prtg_pyprobe.run import main as pyprobe_main
from prtg_pyprobe.utils import config
from prtg_pyprobe.utils.config import configuration_questions
from prtg_pyprobe.utils.defaults import LOG_PATH, CONFIG_PATH


def hash_access_key(key: str) -> str:
    """Hash the access key needed to connect to the PRTG Core.

    Args:
        key (string):  Alphanumeric string.

    Returns:
        string: SHA-1 hashed version of the string.

    """
    key = key.encode("utf-8")
    return hashlib.sha1(key).hexdigest()


def check_systemd():
    """Check if a system uses systemd as startup system.

    Returns:
        bool: True id systemd. False otherwise.

    """
    result = subprocess.run(["ps", "--no-headers", "-o", "comm", "1"], capture_output=True)
    if result.stdout == b"systemd\n":
        return True
    return False


@click.group()
def pyprobe():
    pass


@click.command(name="start")
def dstart():
    """Start a probe daemon."""
    site_packages = get_python_lib()
    work_dir = f"{site_packages}/prtg_pyprobe/"
    click.echo("pyprobe daemon starting")
    with ppd.DaemonContext(
        working_directory=work_dir,
    ):
        pyprobe_main()


@click.command(name="stop")
def dstop():
    """Stop the probe daemon."""
    running_procs = psutil.process_iter()
    for process in running_procs:
        if any("bin/pyprobe" in string for string in process.cmdline()):
            process.terminate()
    click.echo("pyprobe daemon terminated")


@click.command(name="status")
def dstatus():
    """Get status of probe daemon."""
    running_procs = psutil.process_iter()
    for process in running_procs:
        if any("bin/pyprobe" in string for string in process.cmdline()):
            if not any("status" in string for string in process.cmdline()):
                run_since = datetime.datetime.fromtimestamp(process.create_time()).strftime("%Y-%m-%d %H:%M:%S")
                click.echo(f"--- Status {process.name()} ---")
                click.echo(f"PID: {process.pid}")
                click.echo(f"Running as: {process.username()}")
                click.echo(f"Running since: {run_since}")


@click.command()
def configure():
    """Creates or overwrites the configuration.

    Raises:
        KeyboardInterrupt: Keyboard Interrupt is raised to cancel the configuration.

    """
    try:
        if not os.getenv("DEV"):
            if not os.path.exists(LOG_PATH):
                os.mkdir(path=LOG_PATH, mode=666)
            if not os.path.exists(CONFIG_PATH):
                os.mkdir(path=CONFIG_PATH, mode=644)
        config_name = "config.yml"
        if os.path.isfile(f"{CONFIG_PATH}{config_name}"):
            click.echo("\033[93m Completing this config wizard will overwrite your current config! \033[93m")
            cont = PyInquirer.prompt(
                {
                    "type": "confirm",
                    "message": "Do you want to continue?",
                    "name": "continue",
                    "default": True,
                },
            )
            if not cont["continue"]:
                raise KeyboardInterrupt
        answers = PyInquirer.prompt(configuration_questions)
    except KeyboardInterrupt:
        print("Exiting configuration wizard")
        sys.exit(0)
    if answers != {}:
        answers["probe_protocol_version"] = "1"
        answers["probe_access_key_hashed"] = hash_access_key(answers["probe_access_key"])
        probe_cfg = config.ProbeConfig(path=f"{CONFIG_PATH}{config_name}")
        probe_cfg.write(answers)
        click.echo(f"Config written to {CONFIG_PATH}{config_name}")


@click.group()
def daemon():
    pass


@click.group()
def service():
    pass


@click.command(name="install")
def sinstall():
    """Installs the pyprobe service via systemd."""
    if check_systemd():
        site_packages = get_python_lib()
        with open(f"{site_packages}/prtg_pyprobe/utils/pyprobe.service", "r") as fs:
            pyprobe_service = fs.read()
        with open("/etc/systemd/system/pyprobe.service", "w") as fsc:
            pyprobe_service = pyprobe_service.format(
                sys.executable,
                f"{site_packages}/prtg_pyprobe/run.py",
                f"{site_packages}/prtg_pyprobe",
            )
            fsc.write(pyprobe_service)
        subprocess.run(["systemctl", "daemon-reload"])
        subprocess.run(["systemctl", "enable", "pyprobe.service"])
        click.echo("Service install done")
    else:
        click.echo("Service only supported on systems running systemd")


@click.command(name="start")
def sstart():
    """Starts the pyprobe service."""
    if check_systemd():
        subprocess.run(["service", "pyprobe", "start"])
        click.echo("Service started")
    else:
        click.echo("Service only supported on systems running systemd")


@click.command(name="stop")
def sstop():
    """Stops the pyprobe service."""
    if check_systemd():
        subprocess.run(["service", "pyprobe", "stop"])
        click.echo("Service stopped")
    else:
        click.echo("Service only supported on systems running systemd")


@click.command(name="status")
def sstatus():
    """Status of the pyprobe service."""
    if check_systemd():
        subprocess.run(["service", "pyprobe", "status"])
    else:
        click.echo("Service only supported on systems running systemd")


daemon.add_command(dstart)
daemon.add_command(dstop)
daemon.add_command(dstatus)

service.add_command(sinstall)
service.add_command(sstart)
service.add_command(sstop)
service.add_command(sstatus)


pyprobe.add_command(configure)
pyprobe.add_command(service)
pyprobe.add_command(daemon)
