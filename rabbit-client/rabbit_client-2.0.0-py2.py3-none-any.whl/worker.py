async def run(queue, *args, **kwargs):
    while True:
        task = await queue.get()
        await task(*args, **kwargs)
        queue.task_done()
