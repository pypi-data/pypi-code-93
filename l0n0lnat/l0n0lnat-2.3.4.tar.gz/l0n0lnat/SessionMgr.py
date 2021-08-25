class SessionMgr:
    def __init__(self) -> None:
        self.max_id = 0
        self.sessions = {}
        self._closing = False

    async def close(self):
        if self._closing:
            return
        self._closing = True
        for session in self.sessions.values():
            await session.close()
        self.sessions = {}

    def gen_id(self) -> int:
        self.max_id += 1
        return self.max_id

    def add(self, id: int, session) -> None:
        if self._closing:
            return
        self.sessions[id] = session

    def remove(self, id: int) -> None:
        if self._closing:
            return
        try:
            del self.sessions[id]
        except:
            pass

    def get(self, id: int):
        return self.sessions.get(id)
