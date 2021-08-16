from hyperc import solve
from hyperc.models.networking import application, port_80
from hyperc.models.unix.tools import time
from hyperc.models.data_structures import JSON

import flask

assert port_80 in application.listening_ports
assert time.stdout in application.response
assert application.response.type == JSON

solve()
