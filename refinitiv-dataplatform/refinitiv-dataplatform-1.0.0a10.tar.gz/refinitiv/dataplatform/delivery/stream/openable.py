import abc

from .state import State
from .state import StreamState


class Openable(State, abc.ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop = kwargs.get("loop")
        self._next_state = None
        self._prev_state = None
        self._kwargs = None

    def is_open(self):
        return self.state is StreamState.Open

    def is_pause(self):
        return self.state is StreamState.Pause

    def open(self, **kwargs):
        return self._loop.run_until_complete(self.open_async(**kwargs))

    async def open_async(self, **kwargs):
        """ return state of stream """

        if self.state in [StreamState.Pending, StreamState.Open]:
            # it is already opened or is opening
            return self.state

        if self.is_pause():
            self._next_state = StreamState.Open
            self._kwargs = kwargs
            return self.state

        #   call open async
        await self._do_open_async(**kwargs)

        #   done return state
        return self.state

    @abc.abstractmethod
    async def _do_open_async(self, **kwargs):
        # for override
        pass

    def close(self, **kwargs):
        return self._loop.run_until_complete(self.close_async(**kwargs))

    async def close_async(self, **kwargs):
        await self._do_close_async(**kwargs)
        with self._state_lock:
            self._state = StreamState.Closed
        return self.state

    @abc.abstractmethod
    async def _do_close_async(self, **kwargs):
        # for override
        pass

    def pause(self):
        if self.is_pause():
            return self.state

        self._set_pause()
        self._do_pause()

        return self.state

    def _set_pause(self):

        self._prev_state = self.state
        self.state = StreamState.Pause

    @abc.abstractmethod
    def _do_pause(self):
        # for override
        pass

    def resume(self):

        if not self.is_pause():
            return self.state

        self._set_resume()

        if self._next_state is StreamState.Open:
            self.open(self._kwargs)

        self._do_resume()

        return self.state

    def _set_resume(self):
        self.state = self._prev_state

    @abc.abstractmethod
    def _do_resume(self):
        # for override
        pass
