import asyncio
from l0n0lnat.ReverseProto import ReverseProto, ReverseCmd, struct
from l0n0lnat.RemoteServer import RemoteServer
from l0n0lnat.Encryptor import Encryptor


class ReverseSession:
    def __init__(self, owner,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter,
                 enc: Encryptor):
        self.owner = owner
        self.reader = reader
        self.writer = writer
        self.enc = enc
        self.proto = ReverseProto(self, reader, writer, self.enc)

    async def run(self):
        self.proto.heart()
        await self.proto.run()
        await self.on_closed()

    async def close(self):
        if self.writer.is_closing():
            return
        self.writer.close()

    async def on_closed(self):
        if hasattr(self, "tserver"):
            print("Closing Server at port", self.tserver.port)
            await self.tserver.close()
            try:
                del self.owner.remote_servers[self.tserver.port]
            except:
                pass

        if hasattr(self, "remote_session_id"):
            rserver: RemoteServer = self.owner.remote_servers.get(
                self.remote_port)
            if rserver:
                await rserver.on_local_closed(self.remote_session_id)

    async def on_read(self, cmd, data):
        if cmd == ReverseCmd.OpenServer:
            await self.open_server(data)
        elif cmd == ReverseCmd.TransData:
            await self.trans_data(data)
        elif cmd == ReverseCmd.RegistLocal:
            await self.regist_local(data)

    async def open_server(self, data: bytes):
        try:
            target_port = struct.unpack("!I", data)[0]
            pre_server = self.owner.remote_servers.get(target_port)
            if pre_server:
                await self.proto.send(ReverseCmd.PortInUse, b'')
                return
            print("Open Server at port", target_port)
            self.tserver = RemoteServer(self, target_port)
            await self.tserver.start()
            self.owner.remote_servers[target_port] = self.tserver
            self.proto.heart()
        except Exception as e:
            print(e.with_traceback(None))

    async def trans_data(self, data: bytes):
        port, id = struct.unpack("!II", data[:8])
        rserver: RemoteServer = self.owner.remote_servers.get(port)
        if not rserver:
            await self.close()
            return
        await rserver.send_msg_to(id, data[8:])

    async def regist_local(self, data: bytes):
        port, id = struct.unpack("!II", data)
        rserver: RemoteServer = self.owner.remote_servers.get(port)
        if not rserver:
            await self.close()
            return
        await rserver.on_local_connect(id, self)
        self.remote_port = port
        self.remote_session_id = id

    async def on_remote_connect(self, port, id):
        await self.proto.send(ReverseCmd.OnRemoteConnect,
                              struct.pack("!I", id))

    async def on_remote_read(self, id: int, data: bytes):
        await self.proto.send(ReverseCmd.TransData, data)


class ReverseServer:
    def __init__(self,
                 host: str,
                 port: int,
                 enc: Encryptor = Encryptor()):
        self.host = host
        self.port = port
        self.remote_servers = {}
        self.enc = enc

    async def start(self):
        self.server = await asyncio.start_server(
            self.on_connected,
            self.host,
            self.port
        )
        await self.server.start_serving()

    async def on_connected(self,
                           reader: asyncio.StreamReader,
                           writer: asyncio.StreamWriter):
        await ReverseSession(self, reader, writer, self.enc).run()


async def main():
    server = ReverseServer('localhost', 12345)
    await server.start()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
    asyncio.get_event_loop().run_forever()
