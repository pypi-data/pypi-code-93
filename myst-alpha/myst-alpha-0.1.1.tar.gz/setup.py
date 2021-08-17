# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['myst',
 'myst.auth',
 'myst.core',
 'myst.core.data',
 'myst.core.time',
 'myst.data',
 'myst.models',
 'myst.resources']

package_data = \
{'': ['*']}

install_requires = \
['google-auth-oauthlib>=0.4.1,<1.0.0',
 'google-auth>=1.11.0,<2.0.0',
 'httpx>=0.15.4,<0.19.0',
 'importlib-metadata>=4.6.3,<5.0.0',
 'numpy>=1.21.0,<2.0.0',
 'pandas>=1.1.5,<2.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'toml>=0.10.2,<0.11.0',
 'typing-extensions>=3.10.0,<4.0.0',
 'urllib3>=1.24.3,<2.0.0']

setup_kwargs = {
    'name': 'myst-alpha',
    'version': '0.1.1',
    'description': 'This is the official Python library for the Myst Platform.',
    'long_description': '# Myst Python Library\n\nThis is the official Python client library for the Myst Platform.\n\n## Requirements\n\n- Python 3.7+\n\n## Installation\n\nTo install the package from PyPI:\n\n    $ pip install --upgrade myst-alpha\n\n## Authentication\n\nThe Myst API uses JSON Web Tokens (JWTs) to authenticate requests.\n\nThe Myst Python library handles the sending of JWTs to the API automatically and currently supports two ways to authenticate to obtain a JWT: through your Google user account or a Myst service account.\n\n### Authenticating using your user account\n\nIf you don\'t yet have a Google account, you can create one on the [Google Account Signup](https://accounts.google.com/signup) page.\n\nOnce you have access to a Google account, send an email to `support@myst.ai` with your email so we can authorize you to use the Myst Platform.\n\nUse the following code snippet to authenticate using your user account:\n\n```python\nimport myst\n\nmyst.authenticate()\n```\n\nThe first time you run this, you\'ll be presented with a web browser and asked to authorize the Myst Python library to make requests on behalf of your Google user account.\n\n### Authenticating using a service account\n\nYou can also authenticate using a Myst service account. To request a service account, email `support@myst.ai`.\n\nTo authenticate using a service account, set the `MYST_APPLICATION_CREDENTIALS` environment variable to the path to your service account key file:\n\n```sh\n$ export MYST_APPLICATION_CREDENTIALS=</path/to/key/file.json>\n```\n\nThen, go through the service account authentication flow:\n\n```python\nimport myst\n\nmyst.authenticate_with_service_account()\n```\n\nAlternatively, you can explicitly pass the path to your service account key:\n\n```python\nfrom pathlib import Path\n\nimport myst\n\nmyst.authenticate_with_service_account(key_file_path=Path("/path/to/key/file.json"))\n```\n\n## Working with time series\n\nTime series are at the core of Myst\'s API. To retrieve a time series by UUID:\n\n```python\nimport myst\n\n# You\'ll have to replace this UUID with the UUID of a time series you own.\ntime_series = myst.TimeSeries.get("ca2a63d1-3515-47b4-afc7-13c6656dd744")\n```\n\nYou can insert a `TimeArray` into the time series:\n\n```python\nimport myst\nimport numpy as np\n\ntime_array = myst.TimeArray(\n    sample_period="PT1H",\n    start_time="2021-07-01T00:00:00Z",\n    end_time="2021-07-08T00:00:00Z",\n    as_of_time="2021-07-01T00:00:00Z",\n    values=np.random.randn(168),\n)\ntime_series.insert_time_array(time_array=time_array)\n```\n\nYou can also query a time series for a given as of time and natural time range. In this\nexample, the query should return the data we just inserted:\n\n```python\nimport myst\nfrom myst.testing import assert_time_array_equal\n\nreturned_time_array = time_series.query_time_array(\n    start_time=myst.Time("2021-07-01T00:00:00Z"),\n    end_time=myst.Time("2021-07-08T00:00:00Z"),\n    as_of_time=myst.Time("2021-07-01T00:00:00Z"),\n)\nassert_time_array_equal(returned_time_array, time_array)\n```\n\n## Support\n\nFor questions or just to say hi, reach out to `support@myst.ai`.\n',
    'author': 'Myst AI, Inc.',
    'author_email': 'support@myst.ai',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.0,<4.0.0',
}


setup(**setup_kwargs)
