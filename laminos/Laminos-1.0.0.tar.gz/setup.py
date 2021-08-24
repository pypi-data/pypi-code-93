#Amino.py_Remasters_setup_tools

import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="Laminos",
    version="1.0.0 ",
    download_url="https://github.com/ImDefead/Laminos.py",
    description="Laminos refixed amino",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Legion, Fistack, Slavka jup, Mentoru",
    author_email="laminos@inbox.ru",
    license="MIT",
    keywords=[
        
        'Re-bots',
        'Amino-bots',
        'Laminos-bots',
        'capture',
        'captureS'
        'capture-bot',
        'capture-chat',
        'capture-lib',
        'cptr',
        'cptr.co',
        'api',
        'python',
        'python3',
        'python3.x',
        'Legions',
        'Maybes',
        'Dafters',
        'Amino.py',
        'Amino.py',
        'Laminos',
        'laminos.py'
        'L-minos.py',
        'lamino',
        'lamino',
        'laminos-bot',
        'laminos-bots',
        'laminos-bot',
        'ndc',
        'narvii.apps',
        'aminoapps',
        'lamino-py',
        'lamino',
        'lamino-bot',
        'narvii',
        'api',
        'python',
        'python3',
    ],
    include_package_data=True,
    install_requires=[
        'setuptools',
        'requests',
        'websocket-client==0.57.0',
    ],
    setup_requires=[
        'wheel'
    ],
    packages=find_packages(),
)