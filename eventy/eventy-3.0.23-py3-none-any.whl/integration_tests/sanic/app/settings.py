import logging
from enum import Enum

from environs import Env

env = Env()
env.read_env()

logger = logging.getLogger(__name__)

# Logging settings
LOG_LEVEL: str = env.enum(
    'LOG_LEVEL',
    type=Enum('LOG_LEVEL', 'DEBUG INFO WARNING ERROR CRITICAL'),
    ignore_case=True,
    default='INFO',
).name
GKE_LOGGING: bool = env.bool('GKE_LOGGING', False)
COLORED_LOGGING: bool = env.bool('COLORED_LOGGING', False)
SKIP_HEALTHCHECK_LOGGING: bool = env.bool('SKIP_HEALTHCHECK_LOGGING', False)
