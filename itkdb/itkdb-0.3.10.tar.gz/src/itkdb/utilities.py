import logging
import requests

# The background is set with 40 plus the number of the color, and the foreground with 30
# These are the sequences need to get colored ouput
def _get_color_seq(i):
    COLOUR_SEQ = "\033[1;{0:d}m"
    return COLOUR_SEQ.format(30 + i)


# See: https://stackoverflow.com/questions/287871/print-in-terminal-with-colours
# For additional colours, see: https://stackoverflow.com/questions/15580303/python-output-complex-line-with-floats-coloured-by-value
class colours:
    RESET_SEQ = "\033[0m"
    BOLD_SEQ = "\033[1m"
    UNDERLINE_SEQ = '\033[4m'
    BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = list(
        map(_get_color_seq, range(8))
    )


BASE_FORMAT_STRING = "[$BOLD%(asctime)s$RESET][%(levelname)-18s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
FORMAT_STRING = BASE_FORMAT_STRING.replace("$RESET", "").replace("$BOLD", "")
COLOUR_FORMAT_STRING = BASE_FORMAT_STRING.replace("$RESET", colours.RESET_SEQ).replace(
    "$BOLD", colours.BOLD_SEQ
)


class colouredFormatter(logging.Formatter):
    LEVELS = {
        'WARNING': colours.YELLOW,
        'INFO': colours.WHITE,
        'DEBUG': colours.BLUE,
        'CRITICAL': colours.YELLOW,
        'ERROR': colours.RED,
    }

    def __init__(self, msg, use_colour=True):
        logging.Formatter.__init__(self, msg)
        self.use_colour = use_colour

    def format(self, record):
        levelname = record.levelname
        if self.use_colour and levelname in self.LEVELS:
            levelname_colour = self.LEVELS[levelname] + levelname + colours.RESET_SEQ
            record.levelname = levelname_colour
        return logging.Formatter.format(self, record)


# Custom logger class with multiple destinations
class colouredLogger(logging.Logger):
    def __init__(self, name, use_colour=True):
        logging.Logger.__init__(self, name, logging.WARNING)
        colour_formatter = colouredFormatter(
            COLOUR_FORMAT_STRING, use_colour=use_colour
        )
        console = logging.StreamHandler()
        console.setFormatter(colour_formatter)
        self.addHandler(console)
        return


def pretty_print(req):
    request = req.prepare() if isinstance(req, requests.Request) else req
    headers = '\r\n'.join(
        '{}: {}'.format(k, v if k != 'Authorization' else 'Bearer <TOKEN>')
        for k, v in request.headers.items()
    )
    try:
        body = (
            ''
            if request.body is None
            else request.body.decode()
            if isinstance(request.body, bytes)
            else request.body
        )
    except UnicodeDecodeError:
        body = '<Decoding error>'

    return '{method} {path_url} HTTP/1.1\r\n{headers}\r\n\r\n{body}'.format(
        method=request.method, path_url=request.path_url, headers=headers, body=body
    )
