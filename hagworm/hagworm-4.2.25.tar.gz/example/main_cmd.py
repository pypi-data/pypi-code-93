# -*- coding: utf-8 -*-

import os
import sys

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(r'../'))

from hagworm.extend.asyncio.base import Utils, AsyncCirculator
from hagworm.extend.struct import NullData
from hagworm.extend.asyncio.command import Launcher, MainProcessAbstract, ChildProcessAbstract


class MainProcess(MainProcessAbstract):

    async def _run(self):

        self.set_maxsize(len(self._pids))

        self.extend(range(10))

        for _ in self._pids:
            self.append(NullData)

        async for _ in AsyncCirculator():

            stopped = self._check_pids()

            await self.recv_message()

            if stopped:
                break

    async def recv_message(self):

        while True:

            message = await self._pull_server.recv(True)

            if message is None:
                break
            elif message is NullData:
                self.pop_data()
            else:
                self.set_task_done()
                Utils.log.info(f'receive: {message}')

    async def _handle_data(self, data):

        await self._push_server.send(data)


class ChildProcess(ChildProcessAbstract):

    async def _run(self):

        await self._push_client.send(NullData)

        async for _ in AsyncCirculator():

            message = await self._pull_client.recv()

            if message is NullData:

                break

            else:

                await Utils.sleep(Utils.randint(1, 5))

                await self._push_client.send(f'{self._process_id}_{message}')


if __name__ == r'__main__':

    Launcher(subprocess=2, daemon=MainProcess()).run(ChildProcess())
