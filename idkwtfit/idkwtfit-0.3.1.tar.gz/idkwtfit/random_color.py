from random import randrange, randint
from idkwtfit.models.color import RGB, HSL, CMYK


def random_hex() -> str:
    """
    Generate random hex color code

    >>> random_hex()
    175964

    Parameters
     - Nope

    Returns
     - String
    """
    result = ""
    for _ in range(3):
        i = randrange(0, 2 ** 8)
        result += i.to_bytes(1, "big").hex()
    return result


def random_rgb() -> RGB[int]:
    """
    Generate random rgb color code

    >>> random_rgb()
    RGB(R=198, G=82, B=211)

    Parameters
     - Nope

    Returns
     - NamedTuple `RGB`
    """
    return RGB(randint(0, 255), randint(0, 255), randint(0, 255))


def random_hsl() -> HSL[int]:
    """
    Generate random hsl color code

    >>> random_hsl()
    HSL(H=206, S=58, L=2)

    Parameters
     - Nope

    Returns
     - NamedTuple `HSL`
    """
    return HSL(randint(0, 359), randint(0, 100), randint(0, 100))


def random_cmyk() -> CMYK[int]:
    """
    Generate random cmyk color code

    >>> random_cmyk()
    CMYK(C=5, M=71, Y=81, K=93)

    Parameters
     - Nope

    Returns
     - NamedTuple `CMYK`
    """
    return CMYK(randint(0, 100), randint(0, 100), randint(0, 100), randint(0, 100))
