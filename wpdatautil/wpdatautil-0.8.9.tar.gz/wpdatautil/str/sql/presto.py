"""Presto SQL utilities."""
from typing import List


def date_parse(formats: List[str], /, column: str = "{col}") -> str:
    """Return the coalesced date_parse usage expression to parse a column using the given formats.

    Example:
    -------
        date_parse(['%m/%d/%Y %r', '%Y-%m-%d %H:%i:%s', '%Y-%m-%d %H:%i:%s.%f']) ->
            "coalesce(try(date_parse({col}, '%m/%d/%Y %r')), try(date_parse({col}, '%Y-%m-%d %H:%i:%s')), date_parse({col}, '%Y-%m-%d %H:%i:%s.%f'))"

    """
    assert formats

    def _parse(fmt: str, /) -> str:
        return f"date_parse({column}, '{fmt}')"

    if len(formats) == 1:
        return _parse(formats[0])

    return "coalesce(" + ", ".join(f"try({_parse(f)})" for f in formats[:-1]) + ", " + _parse(formats[-1]) + ")"


def base64_hash_id(columns: List[str], /, *, num_bytes: int) -> str:
    """Return an expression of a base64 hash ID corresponding to the given columns having the given length in bytes.

    Example:
    -------
        base64_hash_id(['foo', 'bar', 'coalesce(baz, qux)'], num_bytes=8) -> "to_base64url(substr(sha256(to_utf8(foo || '&' || bar || '&' || coalesce(baz, qux))), -8))"

    """
    assert columns
    assert 1 <= num_bytes <= 32  # This is compatible with sha256.
    return "to_base64url(substr(sha256(to_utf8(" + " || '&' || ".join(columns) + f")), -{num_bytes}))"
