from __future__ import annotations

from pathlib import Path
from typing import Optional, Union

from pydantic import BaseModel


class ArduPilotTestConfig(BaseModel):
    log_dest: Optional[Path] = None
    mission_dest: Optional[Path] = None
