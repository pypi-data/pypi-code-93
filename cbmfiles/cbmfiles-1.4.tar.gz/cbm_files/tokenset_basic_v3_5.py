from .tokensets import _token_set_register
from .tokenset_basic_v2 import TokenSet_BASICv2


_basic_v3_5_tokens = (
    ("RGR", 0xCC),
    ("RLCR", 0xCD),
    ("RLUM", 0xCE),
    ("JOY", 0xCF),
    ("RDOT", 0xD0),
    ("DEC", 0xD1),
    ("HEX$", 0xD2),
    ("ERR$", 0xD3),
    ("INSTR", 0xD4),
    ("ELSE", 0xD5),
    ("RESUME", 0xD6),
    ("TRAP", 0xD7),
    ("TRON", 0xD8),
    ("TROFF", 0xD9),
    ("SOUND", 0xDA),
    ("VOL", 0xDB),
    ("AUTO", 0xDC),
    ("PUDEF", 0xDD),
    ("GRAPHIC", 0xDE),
    ("PAINT", 0xDF),
    ("CHAR", 0xE0),
    ("BOX", 0xE1),
    ("CIRCLE", 0xE2),
    ("GSHAPE", 0xE3),
    ("SSHAPE", 0xE4),
    ("DRAW", 0xE5),
    ("LOCATE", 0xE6),
    ("COLOR", 0xE7),
    ("SCNCLR", 0xE8),
    ("SCALE", 0xE9),
    ("HELP", 0xEA),
    ("DO", 0xEB),
    ("LOOP", 0xEC),
    ("EXIT", 0xED),
    ("DIRECTORY", 0xEE),
    ("DSAVE", 0xEF),
    ("DLOAD", 0xF0),
    ("HEADER", 0xF1),
    ("SCRATCH", 0xF2),
    ("COLLECT", 0xF3),
    ("COPY", 0xF4),
    ("RENAME", 0xF5),
    ("BACKUP", 0xF6),
    ("DELETE", 0xF7),
    ("RENUMBER", 0xF8),
    ("KEY", 0xF9),
    ("MONITOR", 0xFA),
    ("USING", 0xFB),
    ("UNTIL", 0xFC),
    ("WHILE", 0xFD)
    )


class TokenSet_BASICv3_5(TokenSet_BASICv2):
    """Tokens used by BASIC 3.5."""
    def __init__(self):
        super().__init__()
        self.add_tokens(_basic_v3_5_tokens)


_token_set_register['basic-v3.5'] = TokenSet_BASICv3_5()
