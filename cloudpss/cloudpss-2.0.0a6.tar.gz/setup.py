from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
from cloudpss import __version__
setup(
    name='cloudpss',
    version=__version__,
    keywords=("cloudpss", "cloudpss-sdk"),
    description='cloudpss sdk',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT Licence",
    url='https://www.cloudpss.net',
    author='cloudpss',
    author_email='zhangdaming@cloudpss.net',
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    python_requires='>=3.7',
    install_requires=['cffi==1.14.5',
                      'cryptography==3.4.7',
                      'cycler==0.10.0',
                      'pycparser==2.20',
                      'PyJWT==2.1.0',
                      'numpy==1.21.2',
                      'PyYAML==5.4.1',
                      'requests==2.25.1',
                      'websocket-client==0.58.0',
                      'pytz==2021.1'],
)
