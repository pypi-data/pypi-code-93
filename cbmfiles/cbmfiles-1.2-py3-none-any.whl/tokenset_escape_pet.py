from .tokensets import TokenSet


_escape_pet_tokens = (
    ("{stop}", 0x03),
    ("{down}", 0x11),
    ("{rvon}", 0x12),
    ("{home}", 0x13),
    ("{del}", 0x14),
    ("{rght}", 0x1D),
    ("{sret}", 0x8D),
    ("{up}", 0x91),
    ("{rvof}", 0x92),
    ("{clr}", 0x93),
    ("{inst}", 0x94),
    ("{left}", 0x9D)
    )


class TokenSet_EscapePet(TokenSet):
    def __init__(self):
        super().__init__()
        self.raw = True
        self.add_tokens(_escape_pet_tokens)
