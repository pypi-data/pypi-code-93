import asyncio
from asyncio.events import new_event_loop
from l0n0lnat.ReverseProto import ReverseProto, ReverseCmd, struct
from l0n0lnat.LocalClient import LocalClient
from l0n0lnat.SessionMgr import SessionMgr
from l0n0lnat.Encryptor import Encryptor


class ReverseClient:
    def __init__(self,
                 host: str,
                 port: int,
                 localhost: str,
                 localport: int,
                 remoteport: int,
                 enc: Encryptor = Encryptor()):
        self.host = host
        self.port = port
        self.localhost = localhost
        self.localport = localport
        self.remoteport = remoteport
        self.enc = enc
        self.localclient_mgr = SessionMgr()
        self.running = True

    async def start(self):
        while self.running:
            try:
                self.reader, self.writer = await asyncio.open_connection(
                    self.host,
                    self.port
                )
                self.proto = ReverseProto(
                    self, self.reader, self.writer, self.enc)
                self.proto.heart()
                await self.on_connect()
                await self.proto.run()
            except:
                pass
            await self.on_close()
            await asyncio.sleep(1)
            print("Reconnecting ...")

    async def close(self):
        if hasattr(self, "writer"):
            self.writer.close()

    async def on_connect(self):
        await self.proto.send(ReverseCmd.OpenServer,
                              struct.pack("!I", self.remoteport))

    async def on_close(self):
        await self.localclient_mgr.close()

    async def on_read(self, cmd: int, data: bytes):
        if cmd == ReverseCmd.OnRemoteConnect:
            await self.on_remote_connect(data)
        elif cmd == ReverseCmd.PortInUse:
            await self.on_port_inuse(data)

    async def on_remote_connect(self, data: bytes):
        id = struct.unpack("!I", data)[0]
        print(f"Remote Session Conncted. ID = {id}")
        client = LocalClient(id,
                             self,
                             self.localhost,
                             self.localport,
                             self.host,
                             self.port,
                             self.remoteport,
                             self.enc)
        self.localclient_mgr.add(id, client)
        await client.start()

    async def on_port_inuse(self, data: bytes):
        print("Port is in use Exit.")
        await self.close()
        

    async def on_local_client_close(self, id: int):
        self.localclient_mgr.remove(id)


async def main():
    c = ReverseClient('localhost', 12345, 'localhost', 80, 20002)
    await c.start()

if __name__ == "__main__":
    asyncio.get_event_loop().create_task(main())
    asyncio.get_event_loop().run_forever()
