# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['groclimateclient']

package_data = \
{'': ['*']}

install_requires = \
['numpy', 'pandas', 'requests', 'tornado']

setup_kwargs = {
    'name': 'groclimateclient',
    'version': '0.0.0.dev1',
    'description': "Python client library for accessing Gro Intelligence's agricultural data platform",
    'long_description': '<p align="center"><img width="20%" src="https://gro-images.s3.amazonaws.com/Gro-Logo-Emble-Blue-LARGE.svg"></p>\n<h1 align="center">Gro API Client</h1>\n\n\n[![gro-intelligence](https://circleci.com/gh/gro-intelligence/api-client.svg?style=shield)](https://app.circleci.com/pipelines/github/gro-intelligence/api-client?branch=development)\n\n\nThe Gro Intelligence Python API client library provides access to Gro\'s\n[agricultural data platform](https://www.gro-intelligence.com/products/gro-api).\n\nPlease see our developer documentation at\n<https://developers.gro-intelligence.com/> for install instructions, API\nreference documentation, and guides.\n\nThe short version:\n- [Install](https://developers.gro-intelligence.com/installation.html) the\n  library: `pip install groclient` or `conda install -c conda-forge groclient`\n- Get an [API authentication token](https://developers.gro-intelligence.com/authentication.html).\n- Check out the examples below.\n\n## Examples\n\nNavigate to [api/client/samples/](api/client/samples/) and try executing the provided examples.\n\n1. Start with [quick_start.py](api/client/samples/quick_start.py). This script creates an authenticated `GroClient` object and uses the `get_data_series()` and `get_data_points()` methods to find Area Harvested series for Ukrainian Wheat from a variety of different sources and output the time series points to a CSV file. You will likely want to revisit this script as a starting point for building your own scripts.\n\n    Note that the script assumes you have your authentication token set to a `GROAPI_TOKEN` environment variable (see [Saving your token as an environment variable](https://developers.gro-intelligence.com/authentication.html#saving-your-token-as-an-environment-variable)). If you don\'t wish to use environment variables, you can modify the sample script to set [`ACCESS_TOKEN`](https://github.com/gro-intelligence/api-client/blob/0d1aa2bccaa25a033e39712c62363fd89e69eea1/api/client/samples/quick_start.py#L7) in some other way.\n\n    ```sh\n    python quick_start.py\n    ```\n\n    If the API client is installed and your authentication token is set, a csv file called `gro_client_output.csv` should be created in the directory where the script was run.\n\n2. Try out [soybeans.py](api/client/samples/crop_models/soybeans.py) to see the `CropModel` class and its `compute_crop_weighted_series()` method in action. In this example, NDVI ([Normalized difference vegetation index](https://app.gro-intelligence.com/dictionary/items/321)) for provinces in Brazil is weighted against each province\'s historical soybean production to put the latest NDVI values into context. This information is put into a pandas dataframe, the description of which is printed to the console.\n\n    ```sh\n    python crop_models/soybeans.py\n    ```\n\n3. See [brazil_soybeans.ipynb](https://github.com/gro-intelligence/api-client/blob/development/api/client/samples/crop_models/brazil_soybeans.ipynb) for a longer, more detailed demonstration of many of the API\'s capabilities in the form of a Jupyter notebook.\n\n4. You can also use the included `gro_client` tool as a quick way to request a single data series right on the command line. Try the following:\n\n    ```sh\n    gro_client --metric="Production Quantity mass" --item="Corn" --region="United States" --user_email="email@example.com"\n    ```\n\n    The `gro_client` command line interface does a keyword search for the inputs and finds a random matching data series. It displays the data series it picked and the data points to the console. This tool is useful for simple queries, but anything more complex should be done using the provided Python packages.\n',
    'author': 'Gro Intelligence developers',
    'author_email': 'dev@gro-intelligence.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.gro-intelligence.com/products/gro-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
