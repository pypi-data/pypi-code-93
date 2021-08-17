import dict_tools.differ as differ
from typing import Any, Dict, List, Tuple

SERVICE = "ec2"
RESOURCE = "Instance"

TREQ = {
    "absent": {
        "require": [
            "aws.ec2.vpc.absent",
            "aws.ec2.subnet.absent",
            "aws.iam.role.absent",
        ],
        "soft_require": [],
    },
    "present": {
        "require": [
            "aws.ec2.vpc.present",
            "aws.ec2.subnet.present",
            "aws.iam.role.present",
        ],
        "soft_require": [],
    },
}


# TODO Transparent requisites, I.E. All ec2 instances run after all keypairs have been created, networks set up,
#   and iam roles/permissions available
# TODO have this happen before any bootstrapping states


async def absent(hub, ctx, name: str, **kwargs) -> Dict[str, Any]:
    # Get the instance id if it is in the cache, else try to use the name
    instance_map = hub.tool.cache.init.get(ctx, RESOURCE, {})
    instance_id = instance_map.get(name, name)

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=instance_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if not before:
        comment = f"{RESOURCE} '{name}' already absent"
    else:
        try:
            # 'terminate' is an idempotent action
            ret = await hub.tool.boto3.resource.exec(
                resource, "terminate", DryRun=ctx.test, **kwargs
            )
            comment = f"Terminated {RESOURCE}, '{name}'"
            await hub.pop.loop.wrap(resource.wait_until_terminated)
            instance_map.pop(name)
            hub.tool.cache.init.put(ctx, RESOURCE, instance_map)
        except Exception as e:
            return {
                "comment": f"{e.__class__.__name__}: {e}",
                "changes": {},
                "name": name,
                "result": False,
            }

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": True,
    }


async def present(
    hub,
    ctx,
    name: str,
    subnet: str,
    deploy: bool = False,
    bootstrap_plugins: List[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    if bootstrap_plugins is None:
        bootstrap_plugins = []

    # Get the subnet id if it is in the cache, else try to use the name
    subnet_map = hub.tool.cache.init.get(ctx, hub.states.aws.ec2.subnet.RESOURCE, {})
    subnet_id = subnet_map.get(subnet, subnet)
    # At this point we assume the subnet exists

    instance_map = hub.tool.cache.init.get(ctx, RESOURCE, {})
    instance_id = instance_map.get(name, name)

    service = hub.tool.boto3.resource.create(ctx, SERVICE)

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=instance_id)
    before = await hub.tool.boto3.resource.describe(resource)

    if before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            ret = await hub.tool.boto3.resource.exec(
                service,
                "create_instances",
                DryRun=ctx.test,
                MaxCount=1,
                MinCount=1,
                **kwargs,
            )
            instance_map[name] = ret[0].instance_id
            hub.tool.cache.init.put(ctx, RESOURCE, instance_map)
            instance_id = instance_map[name]
            comment = f"Create {RESOURCE}, '{name}'"
        except Exception as e:
            comment = f"{e.__class__.__name__}: {e}"

    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, id=instance_id)
    await hub.pop.loop.wrap(resource.wait_until_exists)

    instance = await hub.tool.boto3.resource.describe(resource)
    # TODO perform modifications as needed
    if deploy:
        for plugin in bootstrap_plugins:
            deploy_ret = await getattr(hub.states.cloud.bootstrap, plugin).run(
                instance["User"],
                ip_address=instance["NetworkInterfaces"][0]["PrivateIPAddress"],
            )
            comment += "\n" + deploy_ret["comment"]
            # TODO use this for bootstrapping to send the master's public key temporarily:
            #   https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2-instance-connect.html#EC2InstanceConnect.Client.send_ssh_public_key

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": bool(after),
    }
