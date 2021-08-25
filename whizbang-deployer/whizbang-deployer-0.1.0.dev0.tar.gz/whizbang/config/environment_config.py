class EnvironmentConfig:
    def __init__(self, environment_config: dict):
        self._environment_config = environment_config

    @property
    def subscription_id(self) -> str: return self._environment_config['subscription_id']
    @property
    def tenant_id(self) -> str: return self._environment_config['tenant_id']
    @property
    def resource_group_name(self) -> str: return self._environment_config['resource_group_name']
    @property
    def resource_group_location(self) -> str: return self._environment_config['resource_group_location']
    @property
    def resource_name_prefix(self) -> str: return self._environment_config['resource_name_prefix']
    @property
    def resource_name_suffix(self) -> str: return self._environment_config['resource_name_suffix']

    # todo - this should not be in environment config, this is solution specific
    @property
    def vnet_address_prefix(self) -> str: return self._environment_config['vnet_address_prefix']

    @property
    def template_name(self) -> str: return self._environment_config['template_name']