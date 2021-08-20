import pathlib
from setuptools import setup

from distutils.core import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()

setup(
    name='alertnow-python',  # How you named your package folder (MyLib)
    packages=['logger'],  # Chose the same as "name"
    version='1.0.2',  # Start with a small number and increase it with every change you make
    license='MIT',  # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    long_description=README,
    long_description_content_type='text/markdown',
    description='This package used for logging information and errors.',  # Give a short description about your library
    author='Tabriz Gulmammadov',  # Type in your name
    author_email='gulmammadovtabriz@gmail.com',  # Type in your E-Mail
    url='https://gitlab.com/log-collector/alertnow-phyton',  # Provide either the link to your github or to your website
    download_url='https://gitlab.com/log-collector/alertnow-phyton/-/archive/main/alertnow-phyton-main.tar.gz',
    # I explain this later on
    keywords=['Log', 'Logger', 'AlertNow'],  # Keywords that define your package best
    install_requires=[  # I get to this in a second
        'requests'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python :: 3',  # Specify which python versions that you want to support
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
