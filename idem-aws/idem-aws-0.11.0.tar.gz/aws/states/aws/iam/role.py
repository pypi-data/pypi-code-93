from dict_tools import differ
from typing import Any, Dict, Tuple

SERVICE = "iam"
RESOURCE = "Role"


async def absent(hub, ctx, name: str, **kwargs) -> Dict[str, Any]:
    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, name=name)
    before = await hub.tool.boto3.resource.describe(resource)

    if not before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            # Attempt to delete the role
            await hub.tool.boto3.resource.exec(resource, "delete", **kwargs)
            comment = f"Delete {RESOURCE}, '{name}'"
        except hub.tool.boto3.exception.ClientError:
            # Role already deleted
            comment = f"{RESOURCE} '{name}' already is absent"

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": not bool(after),
    }


async def present(
    hub, ctx, name: str, assume_role_policy_document: Dict or str, **kwargs
) -> Dict[str, Any]:
    resource = hub.tool.boto3.resource.create(ctx, SERVICE, RESOURCE, name=name)
    before = await hub.tool.boto3.resource.describe(resource)

    if before:
        comment = f"{RESOURCE} '{name}' already exists"
    else:
        try:
            # Attempt to create the Role
            await hub.exec.boto3.client.iam.create_role(
                ctx,
                RoleName=name,
                AssumeRolePolicyDocument=assume_role_policy_document,
                **kwargs,
            )
            comment = f"Created {RESOURCE}, '{name}'"
        except hub.tool.boto3.exception.ClientError as e:
            # Role already deleted
            comment = f"{e.__class__.__name__: {e}}"

    await hub.tool.boto3.client.wait(ctx, SERVICE, "role_exists", RoleName=name)

    # TODO perform other updates as necessary

    after = await hub.tool.boto3.resource.describe(resource)
    return {
        "comment": comment,
        "changes": differ.deep_diff(before, after),
        "name": name,
        "result": bool(after),
    }
