# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['parquet_tools',
 'parquet_tools.commands',
 'parquet_tools.gen_py',
 'parquet_tools.gen_py.parquet',
 'parquet_tools.parquet']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.13.25,<2.0.0',
 'colorama>=0.4.3,<0.5.0',
 'halo>=0.0.29,<0.0.30',
 'pandas>=1.0.4,<2.0.0',
 'pyarrow>=0.17.1,<0.18.0',
 'tabulate>=0.8.7,<0.9.0',
 'thrift>=0.13.0,<0.14.0']

entry_points = \
{'console_scripts': ['parquet-tools = parquet_tools.cli:main']}

setup_kwargs = {
    'name': 'parquet-tools',
    'version': '0.2.7',
    'description': 'Easy install parquet-tools',
    'long_description': '# parquet-tools\n\n![Run Unittest](https://github.com/ktrueda/parquet-tools/workflows/Run%20Unittest/badge.svg)\n![Run CLI test](https://github.com/ktrueda/parquet-tools/workflows/Run%20CLI%20test/badge.svg)\n\nThis is a pip installable [parquet-tools](https://github.com/apache/parquet-mr).\nIn other words, parquet-tools is a CLI tools of [Apache Arrow](https://github.com/apache/arrow).\nYou can show parquet file content/schema on local disk or on Amazon S3.\nIt is incompatible with original parquet-tools.\n\n## Features\n\n- Read Parquet data (local file or file on S3)\n- Read Parquet metadata/schema (local file or file on S3)\n\n## Installation\n\n```bash\n$ pip install parquet-tools\n```\n\n## Usage\n\n```bash\n$ parquet-tools --help\nusage: parquet-tools [-h] {show,csv,inspect} ...\n\nparquet CLI tools\n\npositional arguments:\n  {show,csv,inspect}\n    show              Show human readble format. see `show -h`\n    csv               Cat csv style. see `csv -h`\n    inspect           Inspect parquet file. see `inspect -h`\n\noptional arguments:\n  -h, --help          show this help message and exit\n```\n\n## Usage Examples\n\n#### Show local parquet file\n\n```bash\n$ parquet-tools show test.parquet\n+-------+-------+---------+\n|   one | two   | three   |\n|-------+-------+---------|\n|  -1   | foo   | True    |\n| nan   | bar   | False   |\n|   2.5 | baz   | True    |\n+-------+-------+---------+\n```\n\n#### Show parquet file on S3\n\n```bash\n$ parquet-tools show s3://bucket-name/prefix/*\n+-------+-------+---------+\n|   one | two   | three   |\n|-------+-------+---------|\n|  -1   | foo   | True    |\n| nan   | bar   | False   |\n|   2.5 | baz   | True    |\n+-------+-------+---------+\n```\n\n\n#### Inspect parquet file schema\n\n```bash\n$ parquet-tools inspect /path/to/parquet\n```\n\n<details>\n\n<summary>Inspect output</summary>\n\n```\n############ file meta data ############\ncreated_by: parquet-cpp version 1.5.1-SNAPSHOT\nnum_columns: 3\nnum_rows: 3\nnum_row_groups: 1\nformat_version: 1.0\nserialized_size: 2226\n\n\n############ Columns ############\none\ntwo\nthree\n\n############ Column(one) ############\nname: one\npath: one\nmax_definition_level: 1\nmax_repetition_level: 0\nphysical_type: DOUBLE\nlogical_type: None\nconverted_type (legacy): NONE\n\n############ Column(two) ############\nname: two\npath: two\nmax_definition_level: 1\nmax_repetition_level: 0\nphysical_type: BYTE_ARRAY\nlogical_type: String\nconverted_type (legacy): UTF8\n\n############ Column(three) ############\nname: three\npath: three\nmax_definition_level: 1\nmax_repetition_level: 0\nphysical_type: BOOLEAN\nlogical_type: None\nconverted_type (legacy): NONE\n```\n</details>\n\n#### Cat CSV parquet and transform [csvq](https://github.com/mithrandie/csvq)\n\n```bash\n$ parquet-tools csv s3://bucket-name/test.parquet |csvq "select one, three where three"\n+-------+-------+\n|  one  | three |\n+-------+-------+\n| -1.0  | True  |\n| 2.5   | True  |\n+-------+-------+\n```\n',
    'author': 'Kentaro Ueda',
    'author_email': 'kentaro.ueda.kentaro@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ktrueda/parquet-tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
