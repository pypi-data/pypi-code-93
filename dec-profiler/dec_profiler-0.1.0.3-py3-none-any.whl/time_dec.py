import copy
from functools import wraps
from time import process_time, process_time_ns
from typing import Optional, Any


def _test_time(name: str, measurement_fun, fun, count_loop: int, *args, **kwargs):
    res: Optional[Any] = None

    if count_loop == 1:
        start = measurement_fun()
        res = fun(*args, **kwargs)
        end = measurement_fun()
        print(f"{name}", end - start)
    else:

        arr_res = []

        test_args = copy.deepcopy(args)

        test_kwargs = {}

        for k, v in kwargs.items():
            if k != "no_copy":
                test_kwargs[k] = v

        for x in range(count_loop):
            start = measurement_fun()
            res = fun(*test_args, **test_kwargs)
            end = measurement_fun()
            arr_res.append(end - start)

        print(arr_res)
        print(f"mid {name}", sum(arr_res, 0.0) / len(arr_res))

    return res


def time_s(count_loop=1):
    def wrapper1(fun):
        wraps(fun)

        def wrapper2(*args, **kwargs):
            return _test_time("sec", process_time, fun, count_loop, *args, **kwargs)

        return wrapper2

    return wrapper1


def time_ns(count_loop=1):
    def wrapper1(fun):
        wraps(fun)

        def wrapper2(*args, **kwargs):
            return _test_time("ns", process_time_ns, fun, count_loop, *args, **kwargs)

        return wrapper2

    return wrapper1


if __name__ == '__main__':
    ...
