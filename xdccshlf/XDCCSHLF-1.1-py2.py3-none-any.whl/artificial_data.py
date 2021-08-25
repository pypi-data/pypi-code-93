import random
import string
import csv
from uuid import uuid4


class artificial:

    def __init__(self, num_of_rows):
        self.num_of_rows = num_of_rows

    def _generate_rows(self):

        return [
            [
                ''.join([random.choice(string.ascii_letters) for _ in range(20)]),
                ''.join([random.choice(string.ascii_letters) for _ in range(20)]),
                random.randint(0,100000),
                round(random.random() * random.randint(10, 1000), 4)
            ]

            for _ in range(self.num_of_rows)
        ]

    def generate_csv(self):
        file_name = uuid4().hex + '.csv'
        with open(file_name, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(self._generate_rows())


if __name__ == '__main__':
    a = artificial(10)
    print(a.generate_csv())