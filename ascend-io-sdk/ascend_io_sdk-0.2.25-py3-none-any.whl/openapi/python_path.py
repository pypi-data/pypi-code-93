# At this point, we the openapi_client module is being generated as a
# top-level package, not under the ascend package. We'd like it to be
# under ascend since otherwise it's namespace polutin, but this looks
# a bit complicated to achieve. Instead, we manually move the code to
# the ascend package. However, the code internally expects it to be a
# top level package. So we'll just add the parent namespace to the
# python path when using our code.

import sys
import os

openapi_path = os.path.join(os.path.dirname(__file__), "openapi")
sys.path.insert(0, openapi_path)
