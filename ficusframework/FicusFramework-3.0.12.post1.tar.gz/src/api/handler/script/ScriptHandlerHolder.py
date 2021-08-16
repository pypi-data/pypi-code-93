import threading

holder = threading.local()


def cacheHandler():
    try:
        return holder.key
    except:
        return None
