import os
import socket
from typing import Optional

from foreverbull_core.models.base import Base


class SocketConfig(Base):
    socket_type: str
    host: str = os.getenv("HOSTNAME", socket.gethostname())
    port: int = 0
    listen: bool = True
    recv_timeout: int = 5000
    send_timeout: int = 5000


class Request(Base):
    task: str
    data: Optional[dict] = None


class Response(Base):
    task: str
    error: Optional[str] = None
    data: Optional[dict] = None
