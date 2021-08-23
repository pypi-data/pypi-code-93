from abc import abstractmethod


class A:
    def f(self):
        print('a')


class B:
    g = None

    def f(self):
        print('b')


b = B()
