from hyperc.api import schedule


class CA:
    pass


class CB:
    pa: CA

    def __init__(self):
        self.pa = CA()

    def myact(self):
        ob.pa = oa1

    def myact2(self):
        ob.pa = CA()
        return CA()


oa1 = CA()
ob = CB()


def _run():
    return schedule(goal=lambda ob: ob.pa == oa1)


if __name__ == '__main__':
    _run()
