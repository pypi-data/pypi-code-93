import asyncio
from l0n0lnat.ReverseProto import ReverseProto, ReverseCmd, struct
from l0n0lnat.Encryptor import Encryptor


class LocalClient:
    def __init__(self,
                 id: int,
                 owner,
                 localhost: str,
                 localport: int,
                 remotehost: str,
                 remoteport: int,
                 remote_server_port: int,
                 enc: Encryptor = Encryptor()):
        self.id = id
        self.owner = owner
        self.localhost = localhost
        self.localport = localport
        self.remotehost = remotehost
        self.remoteport = remoteport
        self.remote_server_port = remote_server_port
        self.enc = enc

    async def start(self):
        asyncio.create_task(self._start())

    async def _start(self):
        try:
            self.localreader, self.localwriter = await asyncio.open_connection(
                self.localhost,
                self.localport
            )
            print(
                f"Connected to Local {self.localhost}:{self.localport}, ID = {self.id}")
            self.remotereader, self.remotewriter = await asyncio.open_connection(
                self.remotehost,
                self.remoteport
            )
            self._remote_proto = ReverseProto(
                self,
                self.remotereader,
                self.remotewriter,
                self.enc
            )
            self._remote_proto.heart()
            print(
                f"Connected to Remote {self.remotehost}:{self.remoteport}, ID = {self.id}")
            await self._remote_proto.send(ReverseCmd.RegistLocal,
                                          struct.pack("!II",
                                                      self.remote_server_port,
                                                      self.id))
            asyncio.create_task(self._remote_read())
            asyncio.create_task(self._local_read())
        except Exception as e:
            await self.close()

    async def _remote_read(self):
        await self._remote_proto.run()
        if not self.localwriter.is_closing():
            self.localwriter.close()

    async def _local_read(self):
        try:
            while not self.localwriter.is_closing():
                if self.localreader.at_eof():
                    break

                data = await self.localreader.read(4 * 1024)
                if len(data) == 0:
                    await self.close()
                    break

                await self._remote_proto.send(ReverseCmd.TransData,
                                              struct.pack("!II",
                                                          self.remote_server_port,
                                                          self.id) + data)
        except:
            pass
        if not self.remotewriter.is_closing():
            self.remotewriter.close()

    async def on_read(self, cmd, data: bytes):
        if cmd == ReverseCmd.TransData:
            self.localwriter.write(data)

    async def close(self):
        if hasattr(self, "localwriter") and not self.localwriter.is_closing():
            self.localwriter.close()
            print(
                f"Disconnect from local {self.localhost}:{self.localport}, ID = {self.id}")
        if hasattr(self, "remotewriter") and not self.remotewriter.is_closing():
            self.remotewriter.close()
            print(
                f"Disconnect from Remote {self.remotehost}:{self.remoteport}, ID = {self.id}")
        await self.owner.on_local_client_close(self.id)
        
