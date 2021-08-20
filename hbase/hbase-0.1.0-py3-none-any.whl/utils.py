import base64

from_base64 = lambda s: base64.b64decode(s.encode("ascii")).decode("ascii")
to_base64 = lambda s: base64.b64encode(s.encode("ascii")).decode("ascii")
