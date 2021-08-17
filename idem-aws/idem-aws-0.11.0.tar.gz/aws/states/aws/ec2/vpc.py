import dict_tools.differ as differ
from typing import Any, Dict, Tuple

SERVICE = "ec2"
RESOURCE = "Vpc"
TREQ = {
    "absent": {
        "require": [],
        "soft_require": [],
    },
    "present": {
        "require": [],
        "soft_require": [],
    },
}


async def absent(hub, ctx, name: str, **kwargs) -> Dict[str, Any]:
    # Get the vpc id if it is in the cache, else try to use the name
    vpc_map = hub.tool.cache.init.get(ctx, RESOURCE, {})
    vpc_id = vpc_map.get(name, name)

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=vpc_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if not before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            ret = await hub.tool.boto3.resource.exec(
                resource, "delete", VpcId=vpc_id, **kwargs
            )
            vpc_map.pop(name)
            hub.tool.cache.init.put(ctx, RESOURCE, vpc_map)
            comment = f"Delete {RESOURCE}, '{name}'"
        except Exception as e:
            comment = f"{e.__class__.__name__}: {e}"

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": not after,
    }


async def present(hub, ctx, name: str, cidr_block: str, **kwargs) -> Dict[str, Any]:
    # Get the vpc id if it is in the cache, else try to use the name
    vpc_map = hub.tool.cache.init.get(ctx, RESOURCE, {})
    vpc_id = vpc_map.get(name, name)

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=vpc_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            ret = await hub.exec.boto3.client.ec2.create_vpc(
                ctx, CidrBlock=cidr_block, **kwargs
            )
            vpc_map[name] = ret["ret"][RESOURCE]["VpcId"]
            hub.tool.cache.init.put(ctx, RESOURCE, vpc_map)
            vpc_id = vpc_map[name]
            comment = f"Create {RESOURCE}, '{name}'"
        except Exception as e:
            comment = f"{e.__class__.__name__}: {e}"

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=vpc_id)
    await hub.pop.loop.wrap(resource.wait_until_exists)

    # TODO perform modifications as needed

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": bool(after),
    }
