from typing import Dict

from tktl.commands.validate import build_image
from tktl.core.exceptions.exceptions import MissingDocker
from tktl.core.loggers import LOG, stream_blocking_logs


def run_container(
    path: str,
    nocache: bool,
    background: bool,
    auth_enabled: bool,
    color_logs: bool,
    secrets: Dict = None,
):
    try:
        dm, image = build_image(path, nocache=nocache, secrets=secrets)
    except MissingDocker:
        LOG.log(
            "Couldn't locate docker, please make sure it is installed, or use the DOCKER_HOST environment variable",
            color="red",
        )
        return
    LOG.log("Waiting for service to start...")
    arrow_container, rest_container = dm.run_containers(
        image, detach=True, auth_enabled=auth_enabled
    )

    if background:
        return arrow_container, rest_container
    stream_blocking_logs(arrow_container, rest_container, color_logs=color_logs)
