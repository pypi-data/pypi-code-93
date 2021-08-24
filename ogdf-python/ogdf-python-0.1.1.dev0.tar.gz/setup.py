# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ogdf_python']

package_data = \
{'': ['*']}

install_requires = \
['cppyy>=1.8.1,<2.0.0', 'importlib_resources>=1.4,<2.0']

setup_kwargs = {
    'name': 'ogdf-python',
    'version': '0.1.1.dev0',
    'description': 'Automagic Python Bindings for the Open Graph Drawing Framework written in C++',
    'long_description': 'ogdf-python 0.1.1-dev: Automagic Python Bindings for the Open Graph Drawing Framework\n=====================================================================================\n\n`Original repository <https://github.com/N-Coder/ogdf-python>`_ (GitHub) -\n`Bugtracker and issues <https://github.com/N-Coder/ogdf-python>`_ (GitHub) -\n`PyPi package <https://pypi.python.org/pypi/ogdf-python>`_ (PyPi ``ogdf-python``) -\n`Documentation <https://ogdf-python.readthedocs.io>`_ (Read The Docs).\n\n`Official OGDF website <https://ogdf.net>`_ (ogdf.net) -\n`Public OGDF repository <https://github.com/ogdf/ogdf>`_ (GitHub) -\n`Internal OGDF repository <https://git.tcs.uos.de/ogdf-devs/OGDF>`_ (GitLab) -\n`OGDF Documentation <https://ogdf.github.io/docs/ogdf/>`_ (GitHub / Doxygen) -\n`cppyy Documentation <https://cppyy.readthedocs.io>`_ (Read The Docs).\n\n.. |(TM)| unicode:: U+2122\n\n``ogdf-python`` uses the `black magic <http://www.camillescott.org/2019/04/11/cmake-cppyy/>`_\nof the awesome `cppyy <https://bitbucket.org/wlav/cppyy/src/master/>`_ library to automagically generate python bindings\nfor the C++ Open Graph Drawing Framework (OGDF).\nIt is available for Python>=3.6 and is Apache2 licensed.\nThere are no binding definitions files, no stuff that needs extra compiling, it just works\\ |(TM)|, believe me.\nTemplates, namespaces, cross-language callbacks and inheritance, pythonic iterators and generators, it\'s all there.\nIf you want to learn more about the magic behind the curtains, read `this article <http://www.camillescott.org/2019/04/11/cmake-cppyy/>`_.\n\n\nQuickstart\n----------\n\nFirst, install the package ``ogdf-python`` package.\nPlease note that building ``cppyy`` from sources may take a while.\nIf you didn\'t install OGDF globally on your system,\neither set the ``OGDF_INSTALL_DIR`` to the prefix you configured in ``cmake``,\nor set ``OGDF_BUILD_DIR`` to the subdirectory of your copy of the OGDF repo where your\n`out-of-source build <https://ogdf.github.io/docs/ogdf/md_doc_build.html#autotoc_md4>`_ lives.\n\n.. code-block:: bash\n\n    $ pip install ogdf-python\n    $ OGDF_BUILD_DIR=~/ogdf/build-debug python3\n\nAlternatively, ``ogdf-python`` works very well with Jupyter:\n\n.. code-block:: python\n\n    %env OGDF_BUILD_DIR=~/ogdf/build-debug\n\n    from ogdf_python import ogdf, cppinclude\n    cppinclude("ogdf/basic/graph_generators/randomized.h")\n    cppinclude("ogdf/layered/SugiyamaLayout.h")\n\n    G = ogdf.Graph()\n    ogdf.setSeed(1)\n    ogdf.randomPlanarTriconnectedGraph(G, 20, 40)\n    GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)\n\n    for n in G.nodes:\n        GA.label[n] = "N%s" % n.index()\n\n    SL = ogdf.SugiyamaLayout()\n    SL.call(GA)\n    GA\n\n.. image:: docs/examples/sugiyama-simple.svg\n    :target: docs/examples/sugiyama-simple.ipynb\n    :alt: SugiyamaLayouted Graph\n    :height: 300 px\n\nRead the pitfalls section and check out `docs/examples/pitfalls.ipynb <docs/examples/pitfalls.ipynb>`_\nfor the more advanced Sugiyama example from the OGDF docs.\nThere is also a bigger example in `docs/examples/ogdf-includes.ipynb <docs/examples/ogdf-includes.ipynb>`_.\nIf anything is unclear, check out the python help ``help(ogdf.Graph)`` and read the corresponding OGDF documentation.\n\n..\n    Documentation\n    -------------\n    TODO use ``help(ogdf.Graph)`` and sphinx autodoc\n\n..\n    Load Custom Code\n    ----------------\n    TODO\n\nPitfalls\n--------\n\nSee also `docs/examples/pitfalls.ipynb <docs/examples/pitfalls.ipynb>`_ for full examples.\n\nOGDF sometimes takes ownership of objects (usually when they are passed as modules),\nwhich may conflict with the automatic cppyy garbage collection.\nSet ``__python_owns__ = False`` on those objects to tell cppyy that those objects\ndon\'t need to be garbage collected, but will be cleaned up from the C++ side.\n\n.. code-block:: python\n\n    SL = ogdf.SugiyamaLayout()\n    ohl = ogdf.OptimalHierarchyLayout()\n    ohl.__python_owns__ = False\n    SL.setLayout(ohl)\n\nWhen you overwrite a python variable pointing to a C++ object (and it is the only\npython variable pointing to that object), the C++ object will usually be immediately deleted.\nThis might be a problem if another C++ objects depends on that old object, e.g.\na ``GraphAttributes`` instance depending on a ``Graph`` instance.\nNow the other C++ object has a pointer to a deleted and now invalid location,\nwhich will usually cause issues down the road (e.g. when the dependant object is\ndeleted and wants to deregister from its no longer alive parent).\nThis overwriting might easily happen if you run a Jupyter cell multiple times or some code in a ``for``-loop.\nPlease ensure that you always overwrite or delete dependent C++ variables in\nthe reverse order of their initialization.\n\n.. code-block:: python\n\n    for i in range(5):\n        # clean-up all variables\n        CGA = CG = G = None # note that order is different from C++, CGA will be deleted first, G last\n        # now we can re-use them\n        G = ogdf.Graph()\n        CG = ogdf.ClusterGraph(G)\n        CGA = ogdf.ClusterGraphAttributes(CG, ogdf.ClusterGraphAttributes.all)\n\n        # alternatively manually clean up in the right order\n        del CGA\n        del CG\n        del G\n',
    'author': 'Simon D. Fink',
    'author_email': 'finksim@fim.uni-passau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://ogdf.github.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
