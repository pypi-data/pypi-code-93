import codecs
import logging
import re
import struct

from . import tokensets
from . import tokenset_basic_v2  # noqa: F401
from . import tokenset_basic_v3_5  # noqa: F401
from . import tokenset_basic_v4  # noqa: F401
from . import tokenset_simons_basic  # noqa: F401
from . import tokenset_vic20_super_expander  # noqa: F401
from . import tokenset_vic20_super_expander_jp  # noqa: F401
from . import tokenset_escape_c64  # noqa: F401
from . import tokenset_escape_vic20  # noqa: F401


log = logging.getLogger(__name__)


class BASICFile:
    line_re = re.compile(r'(\d+) *(.*)')

    def __init__(self, fileh, start_addr=None, token_set='basic-v2', encoding='petscii-c64en-uc'):
        if start_addr is None and fileh is not None:
            # read start address from file
            self.start_addr, = struct.unpack('<H', fileh.read(2))
        else:
            self.start_addr = start_addr
        self.lines = {}

        self.token_set = token_set
        try:
            _ = codecs.lookup(encoding)
        except LookupError:
            log.warning("PETSCII codecs not available, using ASCII")
            encoding = 'ascii'
        self.encoding = encoding

        while fileh is not None:
            # link to start of next line (or NULL)
            link, = struct.unpack('<H', fileh.read(2))

            if link == 0:
                # final line, NUL follows
                break

            line_no, = struct.unpack('<H', fileh.read(2))

            # encoded line ends with NUL
            line_encoded = bytearray()
            while True:
                b = fileh.read(1)
                if b == b'\x00':
                    # EOL
                    break
                line_encoded += b

            self.add_encoded_line(line_no, line_encoded)

    def from_text(self, fileh):
        """Tokenize text file."""
        for line in fileh:
            m = self.line_re.match(line.strip())
            if m is None:
                raise ValueError("Syntax error in line: "+line)
            self.add_line(int(m.group(1)), m.group(2))

    def to_binary(self, start_addr=None, prepend_addr=True):
        """Generator to return the program as binary."""
        if start_addr is None:
            start_addr = self.start_addr
        if prepend_addr:
            if start_addr is None:
                raise ValueError("No start address")
            yield struct.pack('<H', start_addr)

        for line_no, line_encoded in self.lines.items():
            start_addr += len(line_encoded) + 5
            yield struct.pack('<HH', start_addr, line_no) + line_encoded + b'\x00'

        yield b'\x00' * 2

    def to_text(self, text_ctrl=True):
        """Generator to return the program as Unicode text."""
        for line_no, line_encoded in self.lines.items():
            yield "{} {}".format(line_no, self.expand(line_encoded, text_ctrl))

    def merge(self, other):
        """Merge the lines of one program into another."""
        for line_no, line_encoded in other.lines.items():
            self.add_encoded_line(line_no, line_encoded)

    def add_line(self, line_no, line):
        """Add a line in the form of text."""
        self.add_encoded_line(line_no, self.tokenize(line))

    def delete_line(self, line_no):
        del self.lines[line_no]

    def add_encoded_line(self, line_no, line_encoded):
        """Add or replace a line in its correct position."""
        self.lines[line_no] = line_encoded
        self.lines = dict(sorted(self.lines.items(), key=lambda x: x[0]))

    @staticmethod
    def escape_set_name(encoding):
        """Return the name of the escape token set based on the encoding name."""
        if '-' in encoding:
            # format is 'petscii-<machine><lang>-<case>'
            machine = encoding.split('-')[1]
            return 'escape-'+machine[:-2]
        return 'escape-c64'

    def tokenize(self, line):
        """Convert a line of text to a binary encoded form."""
        tokenizer = tokensets.lookup(self.token_set)
        escaper = tokensets.lookup(self.escape_set_name(self.encoding))
        ret = bytearray()
        in_quote = False

        current = ''
        for c in line:
            if c == '"':
                if in_quote:
                    current += c
                    # encode text, always converting escapes
                    ret += escaper.tokenize(current, self.encoding)
                    current = ''
                else:
                    # tokenize text
                    ret += tokenizer.tokenize(current, self.encoding)
                    current = c

                in_quote = not in_quote
            else:
                current += c

        if current:
            if in_quote:
                ret += escaper.tokenize(current, self.encoding)
            else:
                ret += tokenizer.tokenize(current, self.encoding)

        return ret

    def expand(self, line_encoded, text_ctrl):
        """Convert a binary encoded line to text."""
        tokenizer = tokensets.lookup(self.token_set)
        escaper = tokensets.lookup(self.escape_set_name(self.encoding))
        ret = ''
        in_quote = False

        current = bytearray()
        for b in line_encoded:
            if b == ord('"'):
                if in_quote:
                    current.append(b)
                    if text_ctrl:
                        # expand escape sequences
                        ret += escaper.expand(current, self.encoding)
                    else:
                        ret += current.decode(self.encoding)
                    current = bytearray()
                else:
                    # expand tokens
                    ret += tokenizer.expand(current, self.encoding)
                    current = bytearray([b])

                in_quote = not in_quote
            else:
                current.append(b)

        if current:
            if in_quote:
                if text_ctrl:
                    ret += escaper.expand(current, self.encoding)
                else:
                    ret += current.decode(self.encoding)
            else:
                ret += tokenizer.expand(current, self.encoding)

        return ret
