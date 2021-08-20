import string
import random

random_word = lambda: "".join(random.choice(string.ascii_letters) for j in range(random.randint(100, 300)))
