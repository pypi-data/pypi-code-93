
from xepmts_endpoints import get_endpoints

GLOBAL_WRITE_ROLES = ["admin", "expert"]
GLOBAL_READ_ROLES = ["read:all"]

def get_domain(global_write_roles=GLOBAL_WRITE_ROLES, global_read_roles=GLOBAL_READ_ROLES, endpoints=None):
    if endpoints is None:
        endpoints = get_endpoints()
    for endpoint in endpoints.values():
        experiment = endpoint.get("experiment", "xenonnt")
        detector = endpoint.get("detector", "tpc")
        
        write_roles = global_write_roles + [f'readWrite{experiment.capitalize()}',  f'readWrite{detector.capitalize()}', f'readWrite{endpoint["resource_title"].title().replace("_", "")}']
        read_roles = write_roles + global_read_roles + [ f'read{experiment.capitalize()}',  f'read{detector.capitalize()}', f'read{endpoint["resource_title"].title().replace("_", "")}']
        
        endpoint["allowed_read_roles"] = endpoint.get("allowed_read_roles", []) + read_roles
        endpoint["allowed_item_read_roles"] = endpoint.get("allowed_item_read_roles", []) + read_roles
        endpoint["allowed_write_roles"] = endpoint.get("allowed_write_roles", []) + write_roles
        endpoint["allowed_item_write_roles"] = endpoint.get("allowed_item_write_roles", []) + write_roles
    return endpoints
    