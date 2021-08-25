try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)


from .meraki_env import meraki_api_key
from .meraki_env import meraki_organization_id
from .meraki_env import meraki_base_url
