from .tokensets import _token_set_register
from .tokenset_basic_v2 import TokenSet_BASICv2


_vic20_super_expander_tokens = (
    ("KEY", 0xCC),
    ("GRAPHIC", 0xCD),
    ("SCNCLR", 0xCE),
    ("CIRCLE", 0xCF),
    ("DRAW", 0xD0),
    ("REGION", 0xD1),
    ("COLOR", 0xD2),
    ("POINT", 0xD3),
    ("SOUND", 0xD4),
    ("CHAR", 0xD5),
    ("PAINT", 0xD6),
    ("RPOT", 0xD7),
    ("RPEN", 0xD8),
    ("RSND", 0xD9),
    ("RCOLR", 0xDA),
    ("RGR", 0xDB),
    ("RJOY", 0xDC),
    ("RDOT", 0xDD)
    )


class TokenSet_VIC20_SuperExpander(TokenSet_BASICv2):
    """Tokens used by Super Expander (VIC-1211A)."""
    def __init__(self):
        super().__init__()
        self.add_tokens(_vic20_super_expander_tokens)


_token_set_register['vic20-super-expander'] = TokenSet_VIC20_SuperExpander()
