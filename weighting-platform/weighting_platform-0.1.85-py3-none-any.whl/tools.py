from traceback import format_exc
from weighting_platform.functions import logging_functions


def round_decorator(round_operator):
    """ Декоратор, оборачивающий оператора раунда взвешивания """
    def wrapper(*args, **kwargs):
        try:
            if args[0].status_ready:
                args[0].status_ready = False
                round_operator(*args, **kwargs)
                args[0].status_ready = True
            else:
                return {"status": False, 'info': 'Раунд в процессе'}
        except:
            logging_functions.fix_round_fail(args[0].gdw, format_exc())
            pass
    return wrapper

