# pylint: disable=W0622
"""cubicweb-counters application packaging information"""

modname = "cubicweb_counters"
distname = "cubicweb-counters"

numversion = (0, 2, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "sequence/counter classes"
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/%s" % distname

__depends__ = {
    "cubicweb": ">=3.33.0,<3.34.0",
}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python :: 3",
]
