import aiohttp
import threading
import asyncio


class Heartbeat:
    def __init__(self, base_url, interval_ms, logger):
        self.base_url = base_url
        self.running = True
        self.thread = None
        self.interval_ms = interval_ms
        self.logger = logger

    async def start(self, task_id):
        try:
            heartbeat_url = f'{self.base_url}/{task_id}'
            self.thread = threading.Thread(name='HearbeatThread', target=self.thread_callback, args=[heartbeat_url])
            self.thread.start()
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e

    def stop(self):
        try:
            if self.running is True:
                thread_name = self.thread.getName()
                self.running = False
                self.logger.info(f'stopping {thread_name} thread')
                # join() will terminate thread when done or rejected
                self.thread.join()
                self.logger.info(f'{thread_name} thread stopped')
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e

    async def send_heartbeat(self, url, interval_ms):
        try:
            while self.running is True:
                await asyncio.sleep(interval_ms)
                async with aiohttp.ClientSession() as session:
                    async with session.post(url) as response:
                        await response.json()
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')

    def thread_callback(self, args):
        loop = asyncio.new_event_loop()
        loop.run_until_complete(self.send_heartbeat(args, self.interval_ms))
        loop.close()
