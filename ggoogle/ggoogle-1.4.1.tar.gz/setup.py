from setuptools import setup, find_packages
from os.path import join, dirname
from pkg_resources import parse_requirements
import utils


setup(
    name='ggoogle',
    version=utils.__version__,
    packages=find_packages(),
    install_requires = [
        'click==8.0.1',
        'selenium==3.141.0',
        'urllib3==1.26.6',
    ],
    setup_requires =  [
        'click==8.0.1',
        'selenium==3.141.0',
        'urllib3==1.26.6',
    ],
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type = 'text/markdown',
    entry_points={
        'console_scripts':
        ['g = utils.__main__:search_in_google']
    },
)
