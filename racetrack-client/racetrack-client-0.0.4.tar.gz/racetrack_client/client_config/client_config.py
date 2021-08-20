from dataclasses import dataclass, field
from typing import Dict


@dataclass
class ClientConfig:
    """Global options for a local client"""

    # API endpoints
    lifecycle_api_url: str = 'http://127.0.0.1:7202'

    # Git auth credentials set for particular repositories
    git_credentials: Dict[str, 'Credentials'] = field(default_factory=dict)


@dataclass
class Credentials:
    username: str
    password: str
