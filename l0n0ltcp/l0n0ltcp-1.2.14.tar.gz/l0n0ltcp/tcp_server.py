import asyncio
import logging
import json
from l0n0ltcp.tcp_callback_base import TcpCallbackBase
from l0n0ltcp.tcp_proto_base import TcpProtoBase
from l0n0ltcp.tcp_session_mgr import TcpSession, TcpSessionMgr


class TcpServer:
    def __init__(self,
                 host: str,
                 port: int,
                 cb: TcpCallbackBase,
                 proto: TcpProtoBase,
                 heartbeat_interval: float = 0,
                 max_no_msg_count: int = 0,
                 loop=None):
        self.loop = loop or asyncio.get_running_loop()
        self.host = host
        self.port = port
        self.server = None
        self.session_mgr = TcpSessionMgr(cb,
                                         proto,
                                         heartbeat_interval,
                                         max_no_msg_count)

    async def _start(self):
        try:
            self.server = await asyncio.start_server(
                client_connected_cb=self.session_mgr.on_new_session,
                host=self.host,
                port=self.port,
                loop=self.loop)
            await self.server.start_serving()
        except Exception as e:
            logging.error(e.with_traceback(None))

    async def _close(self):
        if self.server is not None and self.server.is_serving():
            self.server.close()

    def start(self):
        self.loop.create_task(self._start())

    def close(self):
        self.loop.create_task(self._close())

    def send_msg(self, session_id: int, data: bytes):
        session: TcpSession = self.session_mgr.sessions.get(session_id)
        if session is None:
            logging.error(
                f"[send_msg] not such session! session_id = {session_id}!")
            return False
        return session.send_msg(data)

    def send_json(self, session_id: int, data: dict):
        session: TcpSession = self.session_mgr.sessions.get(session_id)
        if session is None:
            logging.error(
                f"[send_msg] not such session! session_id = {session_id}!")
            return
        session.send_msg(json.dumps(data).encode())
