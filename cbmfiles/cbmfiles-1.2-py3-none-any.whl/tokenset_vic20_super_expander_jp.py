from .tokensets import _token_set_register
from .tokenset_basic_v2 import TokenSet_BASICv2


_vic20_super_expander_jp_tokens = (
    ("HIRES", 0xCC),
    ("SOUND(", 0xCD),
    ("TEXT", 0xCE),
    ("PLOT", 0xCF),
    ("BOX", 0xD0),
    ("CIRCLE", 0xD1),
    ("PAINT", 0xD2),
    ("SETC", 0xD3),
    ("TEMPO", 0xD4),
    ("MUSIC", 0xD5),
    ("KEY", 0xD6),
    ("PIANO", 0xD7),
    ("LOCATE", 0xD8),
    ("CHAR", 0xD9),
    ("RELEASE", 0xDA),
    ("PDL", 0xDB),
    ("JOY", 0xDC),
    ("LIGHTX", 0xDD),
    ("LIGHTY", 0xDE),
    ("POINT", 0xDF),
    ("FGC", 0xE0),
    ("BGC", 0xE1),
    ("BDC", 0xE2)
    )


class TokenSet_VIC20_SuperExpander_JP(TokenSet_BASICv2):
    """Tokens used by Super Expander (VIC-1211/1211M)."""
    def __init__(self):
        super().__init__()
        self.add_tokens(_vic20_super_expander_jp_tokens)


_token_set_register['vic20-super-expander-jp'] = TokenSet_VIC20_SuperExpander_JP()
