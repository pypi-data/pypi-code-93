"""Python 2/3 stuff."""


def win1251(text):
    """Convert to 1251 encoding."""
    try:  # Python 2
        return text.decode('utf-8').encode('windows-1251')
    except AttributeError:  # pragma: no cover
        # Python 3.5+
        return text.encode('windows-1251')


def is_contains(text_1251, utf8_string):
    """Check text with 1251 encoding contains string with utf-8 encoding."""
    try:  # Python 2
        return win1251(utf8_string) in text_1251
    except TypeError:  # pragma: no cover
        # Python 3.5+
        return win1251(utf8_string) in text_1251.encode('windows-1251')


def replace1251(text_1251, utf8_source, utf8_dest):
    """Replace utf8 source string to utf8 destination string in 1251 encoding text."""
    try:  # Python 2
        return text_1251.replace(win1251(utf8_source), win1251(utf8_dest))
    except TypeError:  # pragma: no cover
        # Python 3.5+
        return text_1251.encode('windows-1251').replace(win1251(utf8_source), win1251(utf8_dest))


def gen_next(generator):
    """Next method for generator."""
    try:  # Python 2
        return generator.next()
    except AttributeError:  # pragma: no cover
        # Python 3.5+
        return generator.__next__()


def open_text_file(file_path, mode, encoding):
    """Open text file with encoding."""
    try:  # Python 3.5+
        fhandle = open(file_path, mode + 't', encoding=encoding)
    except TypeError:  # pragma: no cover
        # Python 2
        fhandle = open(file_path, mode + 'b')  # pylint: disable=unspecified-encoding

    return fhandle
