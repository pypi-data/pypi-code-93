import asyncio
import copy
import os
import pathlib
import secrets
import sys
from distutils.version import LooseVersion
from typing import Any
from typing import Dict


async def run(
    hub,
    remotes: Dict[str, Dict[str, str]],
    artifact_version=None,
    **kwargs,
):
    coros = []

    for id_, remote in remotes.items():
        coro = hub.heist.salt.minion.single(
            remote,
            artifact_version=artifact_version,
        )
        coros.append(coro)
    async_kwargs = {"return_exceptions": False}
    if sys.version_info == (3, 6):
        async_kwargs["loop"] = hub.pop.Loop
    await asyncio.gather(*coros, **async_kwargs)


async def single(
    hub,
    remote: Dict[str, Any],
    artifact_version=None,
):
    """
    Execute a single async connection
    """
    # create tunnel
    target_name = secrets.token_hex()
    hub.heist.ROSTERS[target_name] = hub.pop.data.imap(copy.copy(remote))
    tunnel_plugin = remote.get("tunnel", "asyncssh")
    minion_id = remote.get("id")
    bootstrap = remote.get("bootstrap", False)
    await hub.heist.salt.minion.manage_tunnel(
        target_name, tunnel_plugin, remote=remote, bootstrap=bootstrap
    )

    target_os, target_os_arch = await hub.tool.system.os_arch(
        target_name, tunnel_plugin
    )

    repo_data = await hub.artifact.salt.repo_data()
    if isinstance(repo_data, dict) and not artifact_version:
        artifact_version = max(repo_data.keys(), key=lambda x: LooseVersion(x))

    if artifact_version:
        if not await hub.artifact.init.get(
            "salt",
            target_os=target_os,
            version=artifact_version,
            repo_data=repo_data,
        ):
            return False

    # Get salt minion user
    user = remote.get("username")
    if not user:
        user = hub.heist.init.default(target_os, "user")

    run_dir_root = hub.heist.init.default(target_os, "run_dir_root")
    run_dir = hub.tool.path.path_convert(
        target_os,
        run_dir_root,
        (["tmp", f"heist_{user}", f"{secrets.token_hex()[:4]}"]),
    )
    if not hub.tool.path.clean_path(run_dir_root, run_dir):
        hub.log.error(f"The run_dir {run_dir} is not a valid path")
        return False
    hub.heist.CONS[target_name] = {"run_dir": run_dir}

    # Deploy
    binary = hub.artifact.salt.latest("salt", version=artifact_version)
    binary_path = await hub.artifact.salt.deploy(
        target_name,
        tunnel_plugin,
        run_dir,
        binary,
        target_os=target_os,
        minion_id=minion_id,
        bootstrap=bootstrap,
    )
    if not binary_path:
        hub.log.error(f"Could not deploy the artifact to the target {remote['id']}")
        return False

    grains = await hub.salt.call.init.get_grains(target_name, tunnel_plugin, run_dir)
    service_plugin = hub.service.init.get_service_plugin(remote, grains)

    hub.heist.CONS[target_name].update(
        {
            "tunnel_plugin": tunnel_plugin,
            "manager": "salt.minion",
            "service_plugin": service_plugin,
        }
    )
    minion_opts = hub.tool.config.get_minion_opts(
        run_dir=run_dir,
        target_name=target_name,
        target_os=target_os,
        minion_id=minion_id,
        bootstrap=bootstrap,
    )
    await hub.heist.salt.minion.manage_tunnel(
        target_name,
        tunnel_plugin,
        create=False,
        tunnel=True,
        minion_opts=minion_opts,
        bootstrap=bootstrap,
    )

    # generate keys
    if hub.OPT.heist.generate_keys and not bootstrap:
        await hub.salt.key.init.generate_keys(
            target_name,
            tunnel_plugin,
            run_dir,
            minion_id=minion_id,
            target_os=target_os,
        )

    # Start minion
    hub.log.debug(f"Target '{remote.id}' is using service plugin: {service_plugin}")
    await hub.service.salt.minion.start(
        target_name,
        tunnel_plugin,
        service_plugin,
        run_dir=run_dir,
    )

    hub.log.debug(
        f"Starting infinite loop on {remote.id}.  Checkin time: {hub.OPT.heist.checkin_time}"
    )

    while True:
        if not hub.tunnel[tunnel_plugin].connected(target_name):
            # we lost connection, lets check again to see if we can connect
            hub.log.error(f"Lost connection to {minion_id}, trying to reconnect")
            if await hub.heist.salt.minion.manage_tunnel(
                target_name,
                tunnel_plugin,
                remote=remote,
                create=True,
                tunnel=True,
                reconnect=True,
                minion_opts=minion_opts,
            ):
                hub.log.info(f"Reconnected to {minion_id} successfully.")

        await asyncio.sleep(hub.OPT.heist.checkin_time)
        if hub.OPT.heist.dynamic_upgrade:
            latest = hub.artifact.salt.latest("salt")
            if latest != binary:
                binary = latest
                await hub.artifact.salt.update(
                    target_name, tunnel_plugin, latest, binary_path, run_dir
                )


async def clean(hub, target_name, tunnel_plugin, service_plugin, vals):
    """
    Clean up the connections
    """
    # clean up service files
    await hub.service.init.clean(
        target_name, tunnel_plugin, "salt-minion", service_plugin
    )
    # clean up run directory and artifact
    await hub.artifact.init.clean(target_name, tunnel_plugin)

    minion_id = hub.heist.CONS[target_name].get("minion_id")
    if minion_id:
        if not hub.salt.key.init.delete_minion(minion_id):
            hub.log.error(f"Could not delete the key for minion: {minion_id}")


async def manage_tunnel(
    hub,
    target_name,
    tunnel_plugin,
    remote=None,
    create=True,
    tunnel=False,
    reconnect=False,
    minion_opts=None,
    bootstrap=False,
):
    # Create tunnel back to master
    if create:
        created = await hub.tunnel[tunnel_plugin].create(
            target_name, remote, reconnect=reconnect
        )
        if not created:
            hub.log.error(f'Connection to host {remote["host"]} failed')
            return False

        hub.log.info(f'Connection to host {remote["host"]} success')

    if tunnel and not bootstrap:
        import salt.config
        import salt.syspaths

        master_opts = salt.config.client_config(
            pathlib.Path(salt.syspaths.CONFIG_DIR) / "master"
        )
        await hub.tunnel[tunnel_plugin].tunnel(
            target_name,
            minion_opts["publish_port"],
            master_opts.get("publish_port", 4505),
        )
        await hub.tunnel[tunnel_plugin].tunnel(
            target_name,
            minion_opts["master_port"],
            master_opts.get("master_port", 4506),
        )
    return True
