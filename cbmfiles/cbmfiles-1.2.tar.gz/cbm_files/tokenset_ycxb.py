from .tokensets import _token_set_register
from .tokenset_basic_v2 import TokenSet_BASICv2


_basic_ycxb_tokens = (
    ("MODE", 0xCC),
    ("CLB", 0xCD),
    ("CLS", 0xCE),
    ("CLG", 0xCF),
    ("AT", 0xD0),
    ("INK", 0xD1),
    ("AUX", 0xD2),
    ("VDU", 0xD3),
    ("VOL", 0xD4),
    ("CHAN", 0xD5),
    ("SOUND", 0xD6),
    ("SET", 0xD7),
    ("RSET", 0xD8),
    ("GCOL", 0xD9),
    ("HALT", 0xDA),
    ("UDG", 0xDB),
    ("CHAIN", 0xDC),
    ("PUT", 0xDD),
    ("RPT", 0xDE),
    ("INV", 0xDF),
    ("UPS", 0xE0),
    ("DNS", 0xE1),
    ("PLACE", 0xE2),
    ("CHAR", 0xE3),
    ("KEY", 0xE4)
    )


class TokenSet_BASIC_ycxb(TokenSet_BASICv2):
    """Tokens used by Your Computer Extended Basic."""
    def __init__(self):
        super().__init__()
        self.add_tokens(_basic_ycxb_tokens)


_token_set_register['basic-ycxb'] = TokenSet_BASIC_ycxb()
