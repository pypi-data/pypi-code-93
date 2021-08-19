from argparse import ArgumentParser
from . import RelayHTTPRequestHandler
from http.server import HTTPServer
import crayons
from functools import partial


parser = ArgumentParser()
parser.add_argument('from_port', type=int)
parser.add_argument('--to_host', default=None)
parser.add_argument('--to_port', type=int)
parser.add_argument('--timeout', type=float, default=1.0)
parser.add_argument('--show_redirected', action='store_true')

args = parser.parse_args()


patched_handler = partial(
    RelayHTTPRequestHandler,
    to_host=args.to_host,
    to_port=args.to_port,
    timeout=args.timeout,
    show_redirected=args.show_redirected
)

s = HTTPServer(("0.0.0.0", args.from_port), patched_handler)

print(crayons.blue("Interceptor starts with {}s timeout value...".format(args.timeout), bold=True))
print("")
try:
    s.serve_forever()
except KeyboardInterrupt:
    pass
