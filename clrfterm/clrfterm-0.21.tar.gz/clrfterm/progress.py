import sys

import time


class Progress:
    def __init__(self, range_: range) -> None:
        self.range_ = range_

    def __iter__(self):
        for i in self.range_:
            print(f"'\x1b[?25l'\r", end="", file=sys.stdout)
            #yield sys.stdout.write('%d\r' % i)
            yield 1
