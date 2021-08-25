import asyncio
from l0n0lnat.SessionMgr import SessionMgr


class RemoteSession:
    def __init__(self, id: int, owner,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter):
        self.id = id
        self.owner = owner
        self.reader = reader
        self.writer = writer
        self.localsession = None
        self.read_cache = []

    async def send(self, data: bytes):
        if self.writer.is_closing():
            return
        self.writer.write(data)

    async def close(self):
        if self.writer.is_closing():
            return
        self.writer.close()

    async def run(self):
        try:
            while not self.writer.is_closing():
                if self.reader.at_eof():
                    self.writer.close()
                    break

                data = await self.reader.read(4 * 1024)
                if len(data) == 0:
                    self.writer.close()
                    break

                if self.localsession:
                    await self.localsession.on_remote_read(self.id, data)
                else:
                    self.read_cache.append(data)
        except:
            pass
        if self.localsession:
            await self.localsession.close()
            self.localsession = None
        await self.owner.on_session_close(self.id)

    async def on_local_connect(self, session):
        self.localsession = session
        for msg in self.read_cache:
            await self.localsession.on_remote_read(self.id, msg)


class RemoteServer:
    def __init__(self, owner, port):
        self.owner = owner
        self.port = port
        self.remote_session_mgr = SessionMgr()

    async def start(self):
        self.target_server = await asyncio.start_server(
            self.on_session_connect, '0.0.0.0', self.port)
        await self.target_server.start_serving()

    async def close(self):
        await self.remote_session_mgr.close()
        if hasattr(self, "target_server") and self.target_server.is_serving():
            self.target_server.close()

    async def close_session(self, id: int):
        session: RemoteSession = self.remote_session_mgr.get(id)
        if not session:
            return
        session.close()

    async def send_msg_to(self, id: int, data: bytes):
        session: RemoteSession = self.remote_session_mgr.get(id)
        if not session:
            return
        await session.send(data)

    async def on_session_connect(self,
                                 r: asyncio.StreamReader,
                                 w: asyncio.StreamWriter):
        id = self.remote_session_mgr.gen_id()
        print(f"Remote Session Connected. Port = {self.port}, ID = {id}")
        session = RemoteSession(id, self, r, w)
        self.remote_session_mgr.add(id, session)
        await self.owner.on_remote_connect(self.port, id)
        await session.run()

    async def on_session_close(self, id: int):
        print(f"Remote Session Closed. Port = {self.port}, ID = {id}")
        self.remote_session_mgr.remove(id)

    async def on_local_connect(self, id: int, localsession):
        print(f"Local Session Connected. Port = {self.port}, ID = {id}")
        session: RemoteSession = self.remote_session_mgr.get(id)
        if not session:
            return
        await session.on_local_connect(localsession)

    async def on_local_closed(self, id: int):
        print(f"Local Session Closed. Port = {self.port}, ID = {id}")
        session: RemoteSession = self.remote_session_mgr.get(id)
        if not session:
            return
        await session.close()
