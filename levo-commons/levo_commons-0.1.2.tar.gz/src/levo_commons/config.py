from typing import Optional, Tuple

import attr

CONFIG_VERSION = (1, 0)


@attr.s(slots=True)
class PlanConfig:
    """Test plan configuration."""

    spec_path: str = attr.ib(kw_only=True)
    target_url: str = attr.ib(kw_only=True)
    auth: Optional[Tuple[str, str]] = attr.ib(kw_only=True)
    auth_type: str = attr.ib(kw_only=True)
    report_to_saas: bool = attr.ib(kw_only=True)
    # Current config version
    version = CONFIG_VERSION
