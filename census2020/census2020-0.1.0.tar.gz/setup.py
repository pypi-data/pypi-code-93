# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['census2020']

package_data = \
{'': ['*']}

install_requires = \
['StrEnum>=0.4.6,<0.5.0',
 'click>=8.0.1,<9.0.0',
 'pyarrow>=5.0.0,<6.0.0',
 'requests>=2.26.0,<3.0.0',
 'tqdm>=4.62.1,<5.0.0',
 'us>=2.0.2,<3.0.0']

entry_points = \
{'console_scripts': ['census2020 = census2020.cli:cli']}

setup_kwargs = {
    'name': 'census2020',
    'version': '0.1.0',
    'description': 'Some helper functions for working with Census 2020 data',
    'long_description': '# Helper functions for Census 2020 data\n\nEvery decade the US Census Bureau releases data from its [decennial census](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html).\nHowever, the files they provide are quite complicated. And while they provide [SAS](https://www2.census.gov/programs-surveys/decennial/rdo/about/2020-census-program/Phase3/SupportMaterials/2020PL_SAS_import_scripts.zip) and [R](https://www2.census.gov/programs-surveys/decennial/rdo/about/2020-census-program/Phase3/SupportMaterials/2020PL_R_import_scripts.zip), they don\'t provide any help for Python.\n\nThis package provides some convenience functions for playing around with all of this\nCensus data in Python.\n\n## Requirements\n\nWe require Python 3.7.1 or above. This package does use [pyarrow](https://arrow.apache.org/docs/python/install.html) to make manipulating these large data sets easier. However, on some systems, you may encounter installation troubles. If you do, feel free to file an issue!\n\nTo install the package, simply run\n\n```bash\npip install census2020\n```\n\n## Usage\n\n### Getting the data\n\nTo use this package, you should first download the Census data. We\'ve included a simple\nCLI for you to grab all of the data and preprocess it:\n\n```bash\ncensus2020 pull-all --output data\n```\n\nHere `data` is a folder into which all the processed data will be dumped. WARNING: It\ntotals about 1.4GB after it\'s processed.\n\nIf for some reason CLI doesn\'t work, you can pull it by hand as follows:\n\n```python\nfrom pathlib import Path\n\nimport pyarrow.parquet as pq\nimport us\n\nfrom census2020 import downloader\n\noutput_dir = Path("data")\n\nfor state in sorted(set(us.STATES) | {us.states.DC}):\n    print(f"Downloading {state.name}...")\n    table = downloader.get_state(state.abbr)\n    pq.write_table(table, output_dir / f"{state.abbr.lower()}.parquet")\n    print(f"Done with {state.name}")\n```\n\n### Reading the data\n\nReading in all the data into memory can be a bit of a difficult task, so we have\nprovided some interfaces to `pyarrow`\'s filtering features to help.\n\nFor example, suppose you wanted the total population of people who identify as both\nWhite and Asian in all Census Tracts in Kentucky, Indiana, and Ohio. Assuming you\nhave downloaded all the data, you can run the following code:\n\n```python\nfrom census2020 import readers\nfrom census2020.constants import SummaryLevel\n\ndf = readers.read_filtered_dataset(\n    "data",\n    states=["KY", "IN", "OH"],\n    levels=SummaryLevel.STATE_COUNTY_TRACT,\n    columns="P0010013",\n).to_pandas()\n```\n\nHere `"data"` is the location to which you downloaded the Census data.\n\nEach of `states`, `columns`, and `levels` can be either singular values or lists of\nvalues. If no value is specified, then all states, columns, and levels available\nwill be returned.\n\n## License\n\nMIT',
    'author': 'Kevin Wilson',
    'author_email': 'khwilson@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/khwilson/Census2020',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
