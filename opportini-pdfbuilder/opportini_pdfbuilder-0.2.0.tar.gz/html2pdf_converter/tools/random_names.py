import string
import secrets
import numpy as np
from functools import partial


def produce_amount_names(amount_of_names, _randint=np.random.randint):
    names = set()
    pickchar = partial(secrets.choice, string.ascii_lowercase + string.digits)
    while len(names) < amount_of_names:
        names |= {''.join([pickchar() for _ in range(_randint(12, 20))]) for _ in
                  range(amount_of_names - len(names))}
    return names
