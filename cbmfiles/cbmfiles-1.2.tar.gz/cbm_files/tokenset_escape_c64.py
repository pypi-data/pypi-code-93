from .tokensets import _token_set_register
from .tokenset_escape_vic20 import TokenSet_EscapeVIC20


_escape_c64_tokens = (
    ("{orng}", 0x81),
    ("{brn}", 0x95),
    ("{lred}", 0x96),
    ("{gry1}", 0x97),
    ("{gry2}", 0x98),
    ("{lgrn}", 0x99),
    ("{lblu}", 0x9A),
    ("{gry3}", 0x9B)
    )


class TokenSet_EscapeC64(TokenSet_EscapeVIC20):
    def __init__(self):
        super().__init__()
        self.add_tokens(_escape_c64_tokens)


_token_set_register['escape-c64'] = TokenSet_EscapeC64()
