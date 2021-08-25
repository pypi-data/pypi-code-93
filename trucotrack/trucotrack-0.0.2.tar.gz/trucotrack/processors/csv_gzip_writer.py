import gzip

class CsvGzipWriter:
    def __init__(self, file, args):
        self.file = gzip.open(file, 'wb')
        self.header_printed = False
        self.cached = []
        self.size = args.interval

    def write(self, dictionary):
        if len(self.cached) == 0:
            header = ','.join(dictionary.keys())
            self.write_header(header)

        self.cached.append(','.join(dictionary.values()))

        if len(self.cached) >= self.size:
            self.flush()

    def write_header(self, header):
        if not self.header_printed:
            self.file.write(bytearray(header, 'utf-8'))
            self.header_printed = True

    def flush(self):
        cached = self.cached.copy()
        self.cached = []
        for line in cached:
            self.file.write(bytearray(line, 'utf-8'))

    def close(self):
        self.flush()
        self.file.close()
