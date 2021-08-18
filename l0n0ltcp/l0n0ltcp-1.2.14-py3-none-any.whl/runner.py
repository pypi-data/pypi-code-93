import asyncio


def run_forever(loop: asyncio.BaseEventLoop = None):
    loop = loop or asyncio.get_event_loop()
    try:
        print("Press Ctrl+C to Close.")
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        for task in asyncio.all_tasks(loop):
            task.cancel()
        loop.stop()
