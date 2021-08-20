# pylint: disable=W0622
"""cubicweb-rqlcontroller application packaging information"""

modname = "rqlcontroller"
distname = "cubicweb-rqlcontroller"

numversion = (0, 8, 1)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "restfull rql edition capabilities"
web = "http://www.cubicweb.org/project/%s" % distname

__depends__ = {
    "cubicweb": ">= 3.32.2",
}
__recommends__ = {"cubicweb-signedrequest": None}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: JavaScript",
]
