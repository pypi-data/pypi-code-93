import logging


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_object_or_None(model, **kwargs):
    objs = model.objects.filter(**kwargs)
    if objs:
        return objs[0]
    return None


class OnlyDebugLevel(logging.Filter):
    def filter(self, record):
        return record.levelname == 'DEBUG'
