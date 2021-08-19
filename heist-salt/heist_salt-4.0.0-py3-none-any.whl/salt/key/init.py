import asyncio
import pathlib

import salt.config


def accept_minion(hub, minion: str) -> bool:
    return hub.salt.key[hub.OPT.heist.key_plugin].accept_minion(minion)


def delete_minion(hub, minion: str) -> bool:
    return hub.salt.key[hub.OPT.heist.key_plugin].delete_minion(minion)


async def check_pki_dir_empty(
    hub, target_name, tunnel_plugin, key_dir, target_os="linux"
):
    """
    function to check if the pki directory is empty or not
    """
    # TODO: Add windows
    if target_os != "windows":
        check_dir = f'[ "$(ls -A {key_dir})" ]'
        ret = await hub.tunnel[tunnel_plugin].cmd(target_name, check_dir)
        if ret.returncode == 0:
            hub.log.error(
                "The minion pki directory is not empty. Not generating and accepting a key"
            )
            return False
    return True


async def generate_keys(
    hub, target_name, tunnel_plugin, run_dir, minion_id=None, target_os="linux"
):
    binary_path = str(run_dir / "salt")
    if not hub.tool.path.clean_path(
        hub.heist.init.default(target_os, "run_dir_root"), run_dir
    ):
        hub.log.error(f"The path {run_dir} is not valid")
        return False
    key_dir = run_dir / "root_dir" / "etc" / "salt" / "pki" / "minion"
    # mkdir will not add the correct permissions to the parent directories
    # unless each directory is specified
    await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f"mkdir -m700 -p {key_dir.parent.parent.parent} {key_dir.parent.parent} {key_dir.parent} {key_dir}",
    )

    if not await hub.salt.key.init.check_pki_dir_empty(
        target_name, tunnel_plugin, key_dir, target_os=target_os
    ):
        return False

    cmd = f"{binary_path} key --gen-keys=minion --gen-keys-dir={key_dir}"
    ret = await hub.tunnel[tunnel_plugin].cmd(target_name, cmd)
    if ret.returncode != 0:
        return False

    opts = salt.config.client_config(hub.salt.key.local_master.DEFAULT_MASTER_CONFIG)
    minion_key = pathlib.Path(opts["pki_dir"]) / "minions" / minion_id

    await hub.tunnel[tunnel_plugin].get(
        target_name,
        key_dir / f"minion.pub",
        minion_key,
    )
    if not minion_key.is_file():
        hub.log.error("The minion key was not accepted")
        return False

    hub.heist.CONS[target_name].update(
        {
            "minion_id": minion_id,
        }
    )
    return True


async def accept_key_master(hub, target_name, tunnel_plugin, run_dir, minion_id=None):
    """
    Accept the minions key on the salt-master
    """
    if not minion_id:
        hub.log.info("Querying minion id and attempting to accept the minion's key")
        ret = await hub.salt.call.init.get_id(target_name, tunnel_plugin, run_dir)
        if ret.returncode == 0:
            minion_id = ret.stdout.split()[1]
        else:
            hub.log.error("Could not determine the minion_id")
            return False
    retry_key_count = hub.OPT.heist.get("retry_key_count", 5)
    while retry_key_count > 0:
        if hub.salt.key.init.accept_minion(minion_id):
            break
        await asyncio.sleep(5)
        retry_key_count = retry_key_count - 1
    else:
        hub.log.error(f"Could not accept the key for the minion: {minion_id}")
        return False
    hub.heist.CONS[target_name].update(
        {
            "minion_id": minion_id,
        }
    )
    hub.log.info(f"Accepted the key for minion: {minion_id}")
    return True
