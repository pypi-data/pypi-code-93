from .config import override_config_resolver

def setup_module(module):
    override_config_resolver()
