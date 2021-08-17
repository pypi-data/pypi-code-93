import dict_tools.differ as differ
from typing import Any, Dict, Tuple


SERVICE = "ec2"
RESOURCE = "Subnet"
TREQ = {
    "absent": {
        "require": ["aws.ec2.vpc.absent"],
        "soft_require": [],
    },
    "present": {
        "require": [
            "aws.ec2.vpc.present",
        ],
        "soft_require": [],
    },
}


async def absent(hub, ctx, name: str, **kwargs) -> Dict[str, Any]:
    # Get the subnet id if it is in the cache, else try to use the name
    subnet_map = hub.tool.cache.init.get(ctx, RESOURCE, {})
    subnet_id = subnet_map.get(name, name)

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=subnet_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if not before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            ret = await hub.tool.boto3.resource.exec(
                resource, "delete", SubnetId=subnet_id, **kwargs
            )
            subnet_map.pop(name)
            hub.tool.cache.init.put(ctx, RESOURCE, subnet_map)
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


async def present(
    hub, ctx, name: str, cidr_block: str, vpc: str, **kwargs
) -> Dict[str, Any]:
    # Get the vpc id if it is in the cache, else try to use the name
    vpc_map = hub.tool.cache.init.get(ctx, hub.states.aws.ec2.vpc.RESOURCE, {})
    vpc_id = vpc_map.get(vpc, vpc)
    # At this point we assume the vpc exists

    # Get the subnet id if it is in the cache, else try to use the name
    subnet_map = hub.tool.cache.init.get(ctx, RESOURCE, {})
    subnet_id = subnet_map.get(name, name)

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=subnet_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            ret = await hub.exec.boto3.client.ec2.create_subnet(
                ctx, CidrBlock=cidr_block, VpcId=vpc_id, DryRun=ctx.test, **kwargs
            )
            subnet_map[name] = ret["ret"][RESOURCE]["SubnetId"]
            hub.tool.cache.init.put(ctx, RESOURCE, subnet_map)
            subnet_id = subnet_map[name]
            comment = f"Create {RESOURCE}, '{name}'"
        except Exception as e:
            comment = f"{e.__class__.__name__}: {e}"

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=subnet_id)

    # TODO perform modifications as needed

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": bool(after),
    }
