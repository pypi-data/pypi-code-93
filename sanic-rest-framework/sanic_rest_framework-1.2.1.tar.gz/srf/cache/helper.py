import pickle
from srf.utils import run_awaitable


def set_cache(cache_name=None, ex=10, on_user=False):
    def set_fun(func):
        async def call_fun(view, request, *args, **kwargs):
            url_key = request.url
            if on_user and request.user:
                url_key += request+request.user.pk
            res = await request.app.cache.select(cache_name).get(url_key)
            if res:
                return pickle.loads(res)
            res = await run_awaitable(func, view, request, *args, **kwargs)
            await request.app.cache.select(cache_name).set(url_key, pickle.dumps(res), ex)
            return res
        return call_fun
    return set_fun
