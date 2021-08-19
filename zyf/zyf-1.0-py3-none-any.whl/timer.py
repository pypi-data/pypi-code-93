# -*- coding: utf-8 -*-

"""
DateTime   : 2021/02/21 16:41
Author     : ZhangYafei
Description: 函数计时器

使用示例
1. example timeit:

from zyf import timeit

@timeit
def sleep(seconds: int):
    time.sleep(seconds)

>> sleep(1)
Function sleep -> takes 1.001 seconds


2. example repeat_timeit

@repeat_timeit(number=5)
def list_insert_time_test():
    l = []
    for i in range(10000):
        l.insert(0, i)


@repeat_timeit(repeat=3, number=5)
def list_append_time_test():
    l = []
    for i in range(1000000):
        l.append(i)
    return l


@repeat_timeit(number=5, print_detail=True)
def list_gen_time_test():
    l = [i for i in range(1000000)]
    return l


@repeat_timeit(repeat=3, number=5, print_detail=True)
def list_extend_time_test():
    l = []
    for i in range(1000000):
        l.extend([i])


@repeat_timeit(repeat=3, number=5, print_detail=True, print_table=True)
def list_range_time_test():
    l = list(range(1000000))


>> list_insert_time_test()
Function list_insert_time_test -> 5 function calls: average takes 0.097 seconds

>> list_append_time_test()
Function list_append_time_test -> 3 trials with 5 function calls per trial: average trial 3.269 seconds. average function call 0.654 seconds

>> list_gen_time_test()
Time Spend of 5 function calls:
	Function -> list_gen_time_test: total 1.550 seconds, average 0.310 seconds
Average: 0.310 seconds

>> list_extend_time_test()
Time Spend of 3 trials with 5 function calls per trial:
	Function -> list_extend_time_test:
		best: 3.289 seconds, worst: 3.626 seconds, average: 3.442 seconds
Average trial: 3.442 seconds. Average function call: 0.688 seconds

>> list_range_time_test()
Time Spend of 3 trials with 5 function calls per trial:
+----------------------+---------------+---------------+---------------+-----------------------+
|       Function       |   Best trial  |  Worst trial  | Average trial | Average function call |
+----------------------+---------------+---------------+---------------+-----------------------+
| list_range_time_test | 0.640 seconds | 0.714 seconds | 0.677 seconds |     0.135 seconds     |
+----------------------+---------------+---------------+---------------+-----------------------+
"""
import time
from functools import wraps

from prettytable import PrettyTable


def repeat_timeit(repeat: int = 0, number: int = 10, digit: int = 3, print_detail: bool = False,
                  print_table: bool = False):
    def wrap(func):
        """
        装饰器： 判断函数执行时间
        :param func:
        :return:
        """

        @wraps(func)
        def inner(*args, **kwargs):
            func_name, ret = func.__name__, None
            if repeat > 0:
                r = []
                for _ in range(repeat):
                    end, ret = _timeit(func, number, *args, **kwargs)
                    r.append(end)
                min_time, max_time, avg_time = min(r), max(r), sum(r) / repeat
                best_trial_time_string = build_time_print_string(min_time, digit=digit)
                worst_trial_time_string = build_time_print_string(max_time, digit=digit)
                avg_trial_time_string = build_time_print_string(avg_time, digit=digit)
                avg_func_call_time_string = build_time_print_string(avg_time / number, digit)
                if print_table:
                    if print_detail:
                        print(f'Time Spend of {repeat} trials with {number} function calls per trial:')
                        table = PrettyTable(
                            ['Function', 'Best trial', 'Worst trial', 'Average trial', 'Average function call'])
                        table.add_row(
                            [func_name, best_trial_time_string, worst_trial_time_string, avg_trial_time_string,
                             avg_func_call_time_string])
                    else:
                        table = PrettyTable(['Function', 'Average trial', 'Average function call'])
                        table.add_row([func_name, avg_trial_time_string, avg_func_call_time_string])
                    print(table)
                else:
                    if print_detail:
                        print(
                            f'Time Spend of {repeat} trials with {number} function calls per trial:\n\tFunction -> {func_name}: \n\t\tbest: {best_trial_time_string}, worst: {worst_trial_time_string}, average: {avg_trial_time_string}')
                        print(
                            f'Average trial: {avg_trial_time_string}. Average function call: {avg_func_call_time_string}')
                    else:
                        print(
                            f'Function {func_name} -> {repeat} trials with {number} function calls per trial: average trial {avg_trial_time_string}, average function call {avg_func_call_time_string}')

            else:
                end, ret = _timeit(func, number, *args, **kwargs)
                total_time_string = build_time_print_string(end, digit)
                avg_time_string = build_time_print_string(end / number, digit)
                if print_table:
                    if print_detail:
                        print(f'Time Spend of {number} function calls:')
                        table = PrettyTable(['Function', 'Total cost', 'Average cost'])
                        table.add_row([func_name, total_time_string, avg_time_string])
                    else:
                        table = PrettyTable(['Function', 'Average cost'])
                        table.add_row([func_name, avg_time_string])
                    print(table)
                else:
                    if print_detail:
                        print(
                            f'Time Spend of {number} function calls:\n\tFunction -> {func_name}: total {total_time_string}, average {avg_time_string}')
                        print(f'Average: {avg_time_string}')
                    else:
                        print(f'Function {func_name} -> {number} function calls: average takes {avg_time_string}')

            return ret

        return inner

    return wrap


def _timeit(func, number, *args, **kwargs):
    start = time.time()
    num = 1
    while num < number:
        func(*args, **kwargs)
        num += 1
    ret = func(*args, **kwargs)
    end = time.time() - start
    return end, ret


def build_time_print_string(time_seconds: float, digit: int):
    if time_seconds > 60:
        minutes, seconds = divmod(time_seconds, 60)
        return f'{int(minutes)} minutes {seconds:.{digit}f} seconds'
    return f'{time_seconds:.{digit}f} seconds'


def timeit(func):
    """
    装饰器： 判断函数执行时间
    :param func:
    :return:
    """

    @wraps(func)
    def inner(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        end = time.time() - start
        time_string = build_time_print_string(end, digit=3)
        print(f'Function {func.__name__} -> takes {time_string}')
        return ret

    return inner


def Timeit(prefix: str = None, suffix: str = None, decimal: int = 3, print_func_info: bool = False):
    def time_it(func):
        """
        装饰器： 判断函数执行时间
        :param func:
        :return:
        """

        @wraps(func)
        def inner(*args, **kwargs):
            start = time.time()
            ret = func(*args, **kwargs)
            end = time.time() - start
            time_string = build_time_print_string(end, digit=decimal)
            if prefix:
                time_string = f'{prefix} -> takes {time_string}'
            if suffix:
                time_string = f'takes {time_string} -> {suffix}'
            if not prefix and not suffix and print_func_info:
                time_string = f'Function {func.__name__} -> takes {time_string}'
            print(time_string)
            return ret

        return inner

    return time_it
