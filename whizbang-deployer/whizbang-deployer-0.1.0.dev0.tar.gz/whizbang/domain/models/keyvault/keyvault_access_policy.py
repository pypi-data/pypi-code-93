class KeyVaultAccessPolicyPermissions:
    def __init__(self,
                 keys=None,
                 secrets=None,
                 certificates=None,
                 storage=None):
        self.storage: list = storage or []
        self.certificates: list = certificates or []
        self.secrets: list = secrets or []
        self.keys: list = keys or []


class KeyVaultAccessPolicy:
    def __init__(self, name, permissions: dict, object_id=None, lookup_type=None, lookup_value=None, resource_group_name=None):
        self.permissions = KeyVaultAccessPolicyPermissions(**permissions)
        self.lookup_value: str = lookup_value
        self.lookup_type : str = lookup_type
        self.object_id = object_id
        self.name: str = name
        self.resource_group_name: str = resource_group_name
