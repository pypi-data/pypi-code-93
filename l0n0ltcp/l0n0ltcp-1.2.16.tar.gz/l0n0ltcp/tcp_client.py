import asyncio
import json
from l0n0ltcp.runner import regist_client, unregist_client
import logging
from l0n0ltcp.tcp_proto_base import TcpProtoBase
from l0n0ltcp.tcp_session_mgr import TcpSessionMgr
from l0n0ltcp.tcp_callback_base import TcpCallbackBase


class TcpClient:
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
        self.reader = None
        self.writer = None
        self.autoreconnect = False
        self.session_mgr = TcpSessionMgr(cb,
                                         proto,
                                         heartbeat_interval,
                                         max_no_msg_count)
        self.send_buffer = []

    async def _start(self):
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.host, self.port, loop=self.loop)
            regist_client(self)
            await self.session_mgr.on_new_session(self.reader, self.writer, self.send_buffer)
            unregist_client(self)
        except Exception as e:
            logging.error(f"连接[{self.host}:{self.port}]失败!异常:{e.with_traceback(None)}")
        self.send_buffer.clear()

    def start(self):
        self.read_task = self.loop.create_task(self._start())
        self.send_buffer.clear()

    def close(self, unregist = True):
        if hasattr(self, "read_task"):
            self.read_task.cancel()
        self.session_mgr.close()
        self.send_buffer.clear()
        if unregist:
            unregist_client(self)


    def send_msg(self, data: bytes):
        if not self.writer:
            self.send_buffer.append(data)
            return
        if self.writer.is_closing():
            return
        for session in self.session_mgr.sessions.values():
            session.send_msg(data)

    def send_json(self, data: dict):
        return self.send_msg(json.dumps(data).encode())

    def _reconnect_task(self, retry_interval: float):
        if not self.autoreconnect:
            return

        if not self.writer or self.writer.is_closing():
            self.start()

        self.loop.call_later(
            retry_interval, self._reconnect_task, retry_interval)

    def enable_auto_reconnect(self, retry_interval: float):
        self.autoreconnect = True
        self.loop.call_later(
            retry_interval, self._reconnect_task, retry_interval)

    def distable_auto_reconnect(self):
        self.autoreconnect = False
