from .converters import AsyncConverter, SyncConverter


class AsyncStreamer(AsyncConverter):
    async def stream(self, chat_id: int, file: str):
        if chat_id in self.pytgcalls.active_calls:
            self.pytgcalls.change_stream(chat_id, await self.convert(file))
        else:
            self.pytgcalls.join_group_call(chat_id, await self.convert(file))


class SyncStreamer(SyncConverter):
    def stream(self, chat_id: int, file: str):
        if chat_id in self.pytgcalls.active_calls:
            self.pytgcalls.change_stream(chat_id, self.convert(file))
        else:
            self.pytgcalls.join_group_call(chat_id, self.convert(file))
