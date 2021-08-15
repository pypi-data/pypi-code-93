# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['edfi_lms_extractor_lib',
 'edfi_lms_extractor_lib.api',
 'edfi_lms_extractor_lib.csv_generation',
 'edfi_lms_extractor_lib.helpers']

package_data = \
{'': ['*']}

install_requires = \
['SQLAlchemy>=1.3.19,<2.0.0', 'pandas>=1.1.1,<2.0.0', 'xxhash>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'edfi-lms-extractor-lib',
    'version': '1.0.1a0',
    'description': 'Shared functions library for Ed-Fi LMS Extractor projects',
    'long_description': '# Extractor Shared Library\n\nShared library for use in the [Ed-Fi LMS\nToolkit](https://github.com/Ed-Fi-Exchange-OSS/LMS-Toolkit).\n\n## Legal Information\n\nCopyright (c) 2021 Ed-Fi Alliance, LLC and contributors.\n\nLicensed under the [Apache License, Version\n2.0](https://github.com/Ed-Fi-Exchange-OSS/LMS-Toolkit/blob/main/LICENSE) (the\n"License").\n\nUnless required by applicable law or agreed to in writing, software distributed\nunder the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR\nCONDITIONS OF ANY KIND, either express or implied. See the License for the\nspecific language governing permissions and limitations under the License.\n\nSee\n[NOTICES](https://github.com/Ed-Fi-Exchange-OSS/LMS-Toolkit/blob/main/NOTICES.md)\nfor additional copyright and license notifications.\n',
    'author': 'Ed-Fi Alliance, LLC, and contributors',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://techdocs.ed-fi.org/display/EDFITOOLS/LMS+Toolkit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
