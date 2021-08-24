from . import context


def whoami(ctx, refresh, **kwargs):
    return context.get_token(ctx, refresh=refresh)
