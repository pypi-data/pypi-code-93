from .values import Float, Symbol, Record, ImmutableDict, Embedded, preserve
from .values import Annotated, is_annotated, strip_annotations, annotate

from .error import DecodeError, EncodeError, ShortPacket

from .binary import Decoder, Encoder, decode, decode_with_annotations, encode
from .text import Parser, Formatter, parse, parse_with_annotations, stringify

from . import fold

loads = parse
dumps = stringify
