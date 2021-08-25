# pylint: disable=W0622
"""cubicweb-prometheus application packaging information"""


modname = "cubicweb_prometheus"
distname = "cubicweb-prometheus"

numversion = (0, 1, 5)
version = ".".join(str(num) for num in numversion)

license = "LGPL"
author = "LOGILAB S.A. (Paris, FRANCE)"
author_email = "contact@logilab.fr"
description = "Exporting prometheus metrics"
web = "https://forge.extranet.logilab.fr/cubicweb/cubes/%s" % distname

__depends__ = {"cubicweb": ">= 3.27.0", "prometheus-client": ">= 0.10.1"}
__recommends__ = {}

classifiers = [
    "Environment :: Web Environment",
    "Framework :: CubicWeb",
    "Programming Language :: Python :: 3",
    "Programming Language :: JavaScript",
]
