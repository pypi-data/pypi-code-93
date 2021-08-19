from .converters import AsyncConverter, SyncConverter
from youtube_dl import YoutubeDL
from .utils import queues
from typing import Optional
from .utils.queues import que
from pyrogram.types import Message


ydl_opts = {
    "geo-bypass": True,
    "nocheckcertificate": True,
}

ydl = YoutubeDL(ydl_opts)


class AsyncStreamer(AsyncConverter):
    async def stream(self, chat_id: int, file: str, message: Optional[Message]):
        if chat_id in self.pytgcalls.active_calls:
            info = ydl.extract_info(file)
            title = info["title"]
            duration = round(info["duration"] / 120)
            position = await queues.put(chat_id, file=file)
            qeue = que.get(chat_id)
            qeue.append([file])
            await message.reply(f"Judul: [{title}]({file})\nDurasi: {duration}\nDalam Antrian ke: {position}")
            # self.pytgcalls.change_stream(chat_id, await self.convert(file))
        else:
            que[chat_id] = []
            qeue = que["chat_id"]
            qeue.append([file])
            info = ydl.extract_info(file)
            title = info["title"]
            duration = round(info["duration"] / 120)
            try:
                self.pytgcalls.join_group_call(chat_id, await self.convert(file))
            except Exception as e:
                await message.reply(f"Obrolan Suara tidak aktif, dan mendapatkan sebuah error: \n{e}")
                return
            await message.reply(f"Judul: [{title}]({file}\nDurasi: {duration}")


class SyncStreamer(SyncConverter):
    def stream(self, chat_id: int, file: str):
        if chat_id in self.pytgcalls.active_calls:
            self.pytgcalls.change_stream(chat_id, self.convert(file))
        else:
            self.pytgcalls.join_group_call(chat_id, self.convert(file))
