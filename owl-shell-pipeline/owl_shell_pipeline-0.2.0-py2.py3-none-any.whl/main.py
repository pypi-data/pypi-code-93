import os
import subprocess
from pathlib import Path

from distributed import Client
from owl_dev import pipeline
from owl_dev.logging import logger

CMD_SCRIPT = "/tmp/cmd.sh"


def run_command(command, env=None):
    with open(CMD_SCRIPT, "w") as fh:
        fh.write(command)
    os.chmod(CMD_SCRIPT, 0o744)

    res = subprocess.run(
        CMD_SCRIPT,
        env=env,
        cwd=Path.home(),
        shell=True,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    return res


@pipeline
def main(
    *, command: str, use_dask: bool, output_dir: Path = None, **kwargs,
):
    logger.info("Pipeline started")
    client = Client.current()

    if use_dask:
        scheduler = client._scheduler_identity["address"]
        logger.info("Using Dask scheduler at %s", scheduler)
        env = {"DASK_SCHEDULER_ADDRESS": client._scheduler_identity["address"]}
        res = run_command(command, env=env)
    else:
        fut = client.submit(run_command, command)
        res = client.gather(fut)

    if res.returncode == 0:
        logger.info("Command successful : %s", res.stdout.decode())
    else:
        logger.error("Command failed : %s", res.stderr.decode())
        raise Exception("Command failed")

    return res.returncode
