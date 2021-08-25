import struct
import asyncio
from enum import IntEnum
from l0n0lnat.Encryptor import Encryptor
# size 4字节，cmd 4字节，data n字节


class ReverseProto:
    def __init__(self, owner,
                 reader: asyncio.StreamReader,
                 writer: asyncio.StreamWriter,
                 enc: Encryptor):
        self.owner = owner
        self.reader = reader
        self.writer = writer
        self.status = 0
        self.enc = enc
        self.no_msg_count = 0

    def heart(self):
        if self.writer.is_closing():
            return
        self.no_msg_count += 1
        if self.no_msg_count >= 10:
            asyncio.create_task(self.owner.close())
            return
        asyncio.create_task(self.send(ReverseCmd.Heart, b'hello'))
        asyncio.get_event_loop().call_later(1, self.heart)

    async def run(self):
        try:
            while not self.writer.is_closing():
                header = await self.reader.readexactly(8)
                size, cmd = struct.unpack("!II", header)
                data = await self.reader.readexactly(size)
                data = self.enc.decode(data)
                self.no_msg_count = 0
                await self.owner.on_read(cmd, data)
        except:
            pass
        await self.owner.close()

    async def send(self, cmd: int, data: bytes):
        if self.writer.is_closing():
            return
        data = self.enc.encode(data)
        self.writer.write(struct.pack("!II", len(data), cmd))
        self.writer.write(data)
        await self.writer.drain()


class ReverseCmd(IntEnum):
    OpenServer = 1              # 服务器开一个服务器，监听某端口
    OnRemoteConnect = 2         # 开的服务器被连接了，开两个连接，一个连接到本地服务，一个连接到服务器用于传输数据
    TransData = 3               # 传输 用户数据
    RegistLocal = 4
    PortInUse = 5
    Heart = 6
