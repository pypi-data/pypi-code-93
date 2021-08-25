"""Compliance with NationStates' API and web rate limits."""

# This is not the exact algorithm NationStates uses for ratelimiting;
# rather it's the best compromise between usability and developer
# sanity.

import asyncio


def _create_ratelimiter(requests, per):
    loop = asyncio.get_event_loop()

    semaphore = asyncio.BoundedSemaphore(requests)
    portion_duration = per * 1.1  # account for the Universe being imperfect

    def decorator(func):
        async def wrapper(*args, **kwargs):
            await semaphore.acquire()
            try:
                resp = await func(*args, **kwargs)
            finally:
                loop.call_later(portion_duration, semaphore.release)
            return resp
        return wrapper
    return decorator


# "API Rate Limit: 50 requests per 30 seconds."
# https://www.nationstates.net/pages/api.html#ratelimits
api = _create_ratelimiter(requests=50, per=30)

# "Scripts must send no more than 10 requests per minute."
# https://forum.nationstates.net/viewtopic.php?p=16394966#p16394966
web = _create_ratelimiter(requests=10, per=60)

_web_restricted_lock = asyncio.Lock()

# "A tool may not execute restricted actions simultaneously, but must
#  instead wait for the completion of each command--that is, a complete
#  response from the NationStates server--before issuing the next one."
# https://forum.nationstates.net/viewtopic.php?p=16394966#p16394966
def web_restricted(func):
    async def wrapper(*args, **kwargs):
        async with _web_restricted_lock:
            resp = await func(*args, **kwargs)
        return resp
    return wrapper
