import sys

import noid.utils
from noid import pynoid

# print(pynoid.validate('iAm8W4b'))
string = "6Fok8j"
for x in noid.utils.XDIGIT:
    print(f"{string}{x} is {pynoid.validate(f'{string}{x}')}")
