""" Пакет включает все функции для работы со шлагбаумами """
from weighting_platform.functions import general_functions


def barrier_func_decorator(func):
    """ Декоратор, оборачивающий все функции работы со шлагбаумами """
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
    return wrapper


@barrier_func_decorator
def open_barrier(qsb, course):
    """ Формирует и передает комманду в QSB для открытия шлагбаума, исходя из
    заданного направления"""
    barrier_name = general_functions.form_point_name(course, 'BARRIER')
    response = qsb.unlock_point(barrier_name)
    barrier_status(course, 'opening')
    return response


@barrier_func_decorator
def close_barrier(qsb, course):
    """ Формирует и передает команду в QSB для закрытия шлагбаума, исходя из
    заданного направления """
    barrier_name = general_functions.form_point_name(course, 'BARRIER')
    response = qsb.lock_point(barrier_name)
    barrier_status(course, 'closing')
    return response


def barrier_status(course, state, tag=None, qpi=None, *args, **kwargs):
    """ Вызывает status для операций со шлагбаумами """
    barrier_name = general_functions.form_point_name(course, 'BARRIER')
    status = "BARRIER_CHANGE_{}_{}".format(barrier_name, state)
    msg = {'COURSE': course.upper(),
           'STATUS': status.upper(),
           'TAG': tag}
    for k, v in kwargs.items():
        msg[k] = v
    general_functions.send_status(msg, qpi)
    return msg


