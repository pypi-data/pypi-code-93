import json


async def get_grains(hub, target_name, tunnel_plugin, run_dir, target_os="linux"):
    """
    Run grains.items and return the grains as a dictionary.
    """
    binary_path = run_dir / "salt"
    grains = await hub.tunnel[tunnel_plugin].cmd(
        target_name,
        f"{binary_path} call --config-dir {run_dir} --local grains.items --out json",
    )
    return json.loads(grains.stdout)["local"]


async def get_id(hub, target_name, tunnel_plugin, run_dir, target_os="linux"):
    binary_path = run_dir / "salt"
    return await hub.tunnel[tunnel_plugin].cmd(
        target_name, f"{binary_path} call --config-dir {run_dir} --local grains.get id"
    )
