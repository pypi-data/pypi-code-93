import time


def time_s(count_loop=1):
    def wrapper1(fun):
        def wrapper2(*args, **kwargs):
            if count_loop == 1:
                start = time.process_time()
                fun(*args, kwargs)
                end = time.process_time()
                print("ns", end - start)
            else:

                arr_res = []
                for x in range(count_loop):
                    start = time.process_time()
                    fun(*args, **kwargs)
                    end = time.process_time()
                    arr_res.append(end - start)

                print(arr_res)
                print("mid ns", sum(arr_res, 0.0) / len(arr_res))

        return wrapper2

    return wrapper1


def time_ns(count_loop=1):
    def wrapper1(fun):
        def wrapper2(*args, **kwargs):
            if count_loop == 1:
                start = time.process_time_ns()
                fun(*args, kwargs)
                end = time.process_time_ns()
                print("ns", end - start)
            else:

                arr_res = []
                for x in range(count_loop):
                    start = time.process_time_ns()
                    fun(*args, **kwargs)
                    end = time.process_time_ns()
                    arr_res.append(end - start)

                print(arr_res)
                print("mid ns", sum(arr_res, 0.0) / len(arr_res))

        return wrapper2

    return wrapper1


if __name__ == '__main__':
    ...
