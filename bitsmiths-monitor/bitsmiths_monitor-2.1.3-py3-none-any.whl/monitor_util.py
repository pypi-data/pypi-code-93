from .braze import bLazyLoad


def append_lazy_load(ll: bLazyLoad) -> str:
    res = ''

    if ll:
        if ll.limit <= 0 or ll.limit > 10000:
            ll.limit = 10000

        res += ' limit %d' % ll.limit

        if ll.offset:
            res += ' offset %d' % ll.offset

    return res
