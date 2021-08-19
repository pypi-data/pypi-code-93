# Use a local Salt master's keys to accept a minion key
import os
import pathlib

import salt.config
import salt.key
import salt.syspaths


def __init__(hub):
    hub.salt.key.local_master.DEFAULT_MASTER_CONFIG = os.path.join(
        salt.syspaths.CONFIG_DIR, "master"
    )


def accept_minion(hub, minion: str) -> bool:
    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    with salt.key.get_key(opts) as salt_key:
        if minion not in salt_key.list_status("all")["minions_pre"]:
            return False

        salt_key.accept(
            match=[
                minion,
            ],
            include_denied=False,
            include_rejected=False,
        )

    return minion in salt_key.list_status("accepted")["minions"]


def delete_minion(hub, minion: str) -> bool:
    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    with salt.key.get_key(opts) as salt_key:
        if minion not in salt_key.list_status("all")["minions"]:
            hub.log.debug(f"The minion `{minion}` is already denied")
            return True

        salt_key.delete_key(
            match=[
                minion,
            ],
            preserve_minions=None,
            revoke_auth=False,
        )

    return minion not in salt_key.list_status("all")["minions"]
