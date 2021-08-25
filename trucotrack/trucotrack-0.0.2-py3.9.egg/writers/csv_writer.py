import csv

class CSVWriter:
    def __init__(self, args):
        self.file = open(args.output, 'w')
        self.header_printed = False
        self.cached = []
        self.size = args.interval

    def write(self, dictionary):
        if len(self.cached) == 0:
            fieldnames = list(dictionary.keys())
            self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
            self.print_header()

        self.cached.append(dictionary)

        if len(self.cached) >= self.size:
            self.flush()

    def print_header(self):
        if not self.header_printed:
            self.writer.writeheader()
            self.header_printed = True

    def flush(self):
        cached = self.cached.copy()
        self.cached = []
        for dictionary in cached:
            self.writer.writerow(dictionary)

    def close(self):
        self.flush()
        self.file.close()
