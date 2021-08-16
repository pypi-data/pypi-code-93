from datetime import datetime

from setuptools import find_packages, setup

from common_setup import common_setup_kwargs, DESCRIPTION_TEMPLATE, version

# weekly releases use a date for their "version"
version = version.split("b")[0]  # PyPI disallows 'b' unless followed by [.postN][.devN]
version += datetime.today().strftime(".%Y.%m.%d")

description = DESCRIPTION_TEMPLATE.format(
    package_name="datarobot_early_access",
    pypi_url_target="https://pypi.python.org/pypi/datarobot-early-access/",
    extra_desc=(
        'This package is the "early access" version of the client. For the most stable version, see'
        " the quarterly release on PyPI at https://pypi.org/project/datarobot/."
    ),
    pip_package_name="datarobot_early_access",
    docs_link="https://datarobot-public-api-client.readthedocs-hosted.com/en/early-access/",
)

packages = find_packages(exclude=["tests*"])

common_setup_kwargs.update(
    name="datarobot_early_access", version=version, packages=packages, long_description=description,
)

setup(**common_setup_kwargs)
