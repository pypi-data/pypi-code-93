# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['strictdoc',
 'strictdoc.backend',
 'strictdoc.backend.dsl',
 'strictdoc.backend.dsl.errors',
 'strictdoc.backend.dsl.models',
 'strictdoc.backend.source_file_syntax',
 'strictdoc.cli',
 'strictdoc.core',
 'strictdoc.core.actions',
 'strictdoc.core.finders',
 'strictdoc.export.excel',
 'strictdoc.export.html',
 'strictdoc.export.html.generators',
 'strictdoc.export.html.renderers',
 'strictdoc.export.html.tools',
 'strictdoc.export.rst',
 'strictdoc.helpers']

package_data = \
{'': ['*'],
 'strictdoc.export.html': ['_static/*',
                           '_static_extra/mathjax/*',
                           '_static_extra/mathjax/output/chtml/fonts/*',
                           '_static_extra/mathjax/output/chtml/fonts/woff-v2/*',
                           'templates/*',
                           'templates/_shared/*',
                           'templates/_shared/requirement_block/*',
                           'templates/document_tree/*',
                           'templates/requirements_coverage/*',
                           'templates/single_document/*',
                           'templates/single_document_table/*',
                           'templates/single_document_traceability/*',
                           'templates/single_document_traceability_deep/*',
                           'templates/source_file_coverage/*',
                           'templates/source_file_view/*']}

install_requires = \
['XlsxWriter>=1.3.7,<2.0.0',
 'beautifulsoup4>=4.9.3,<5.0.0',
 'docutils>=0.16,<0.17',
 'jinja2>=2.11.2,<3.0.0',
 'python-datauri>=0.2.9,<0.3.0',
 'textx==2.3.0']

entry_points = \
{'console_scripts': ['strictdoc = strictdoc.cli.main:main']}

setup_kwargs = {
    'name': 'strictdoc',
    'version': '0.0.13',
    'description': ' Software for writing technical requirements and specifications.',
    'long_description': '# StrictDoc\n\n![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20macOS/badge.svg?branch=master)\n![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20Linux/badge.svg?branch=master)\n![](https://github.com/stanislaw/strictdoc/workflows/StrictDoc%20on%20Windows/badge.svg?branch=master)\n\nStrictDoc is software for writing technical requirements and specifications.\n\nSummary of StrictDoc features:\n\n- The documentation files are stored as human-readable text files.\n- A simple domain-specific language DSL is used for writing the documents. The\n  text format for encoding this language is called SDoc (strict-doc).\n- StrictDoc reads `*.sdoc` files and builds an in-memory representation of the\n  document tree.\n- From this in-memory representation, StrictDoc can generate the documentation\n  into a number of formats including HTML, RST, PDF, Excel.\n- The focus of the tool is modeling requirements and specifications documents.\n  Such documents consist of multiple statements like "system X shall do Y"\n  called requirements.\n- The requirements can be linked together to form the relationships, such as\n  "parent-child", and from these connections, many useful features, such as\n  [Requirements Traceability](https://en.wikipedia.org/wiki/Requirements_traceability)\n  and Documentation Coverage, can be derived.\n- Good performance of the [textX](https://github.com/textX/textX) parser and\n  parallelized incremental generation of documents: generation of document trees\n  with up to 2000-3000 requirements into HTML pages stays within a few seconds.\n  From the second run, only changed documents are regenerated. Further\n  performance tuning should be possible.\n\n**Warning:** The StrictDoc project is alpha quality. See the\n[Roadmap](https://strictdoc.readthedocs.io/en/latest/StrictDoc.html#roadmap)\nsection to get an idea of the overall project direction.\n\nThe documentation is hosted on Read the Docs:\n[StrictDoc documentation](https://strictdoc.readthedocs.io/en/latest/).\n',
    'author': 'Stanislav Pankevich',
    'author_email': 's.pankevich@gmail.com',
    'maintainer': 'Stanislav Pankevich',
    'maintainer_email': 's.pankevich@gmail.com',
    'url': 'https://github.com/stanislaw/strictdoc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
