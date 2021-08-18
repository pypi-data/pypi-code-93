""" Пустой документ для тестов """

def test_decorator(func, *args, **kwargs):
    def wrapper(*args, **kwargs):
        print("BEGIN")
        func('32')
        print("END")
    return wrapper



@test_decorator
def foo(some):
    print("SOME:", some)


foo(33)
