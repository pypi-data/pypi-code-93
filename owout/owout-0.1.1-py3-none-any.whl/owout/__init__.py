import sys

from pyowo import owo


class NewSTDOUT:
    def __init__(self, stdout) -> None:
        self.stdout = stdout

    def __getattr__(self, name):
        if name == "write":
            return self.write
        return getattr(self.stdout, name)

    def write(self, data, *args) -> None:
        data = owo(data)
        self.stdout.write(data)


sys.stdout = NewSTDOUT(sys.stdout)
sys.stderr = NewSTDOUT(sys.stderr)
