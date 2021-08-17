from .tokensets import _token_set_register
from .tokenset_basic_v2 import TokenSet_BASICv2


_basic_v4_tokens = (
    ("CONCAT", 0xCC),
    ("DOPEN", 0xCD),
    ("DCLOSE", 0xCE),
    ("RECORD", 0xCF),
    ("HEADER", 0xD0),
    ("COLLECT", 0xD1),
    ("BACKUP", 0xD2),
    ("COPY", 0xD3),
    ("APPEND", 0xD4),
    ("DSAVE", 0xD5),
    ("DLOAD", 0xD6),
    ("CATALOG", 0xD7),
    ("RENAME", 0xD8),
    ("SCRATCH", 0xD9),
    ("DIRECTORY", 0xDA),
    ("DCLEAR", 0xDB),
    ("BANK", 0xDC),
    ("BLOAD", 0xDD),
    ("BSAVE", 0xDE)
    )


class TokenSet_BASICv4(TokenSet_BASICv2):
    """Tokens used by BASIC 4.0."""
    def __init__(self):
        super().__init__()
        self.add_tokens(_basic_v4_tokens)


_token_set_register['basic-v4'] = TokenSet_BASICv4()
