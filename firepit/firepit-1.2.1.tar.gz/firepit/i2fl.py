import ujson

class JsonIO:
    """Convert an iterable of JSON-serializable objects to a file-like object"""

    def __init__(self, d):
        self.it = iter(d)
        self.buf = ''

    def __iter__(self):
        return self

    def __next__(self):
        r = self.readline()
        if not r:
            raise StopIteration
        return r

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

    def close(self):
        self.buf = ''

    def read(self, n):
        result = ''
        try:
            while n > len(self.buf):
                self.buf += ujson.dumps(next(self.it))
            result = self.buf[:n]
            self.buf = self.buf[n:]
        except StopIteration:
            result = self.buf
            self.buf = ''
        return result

    def readline(self, size=None):
        self.buf += ujson.dumps(next(self.it))
        result = self.buf
        self.buf = ''
        return result
