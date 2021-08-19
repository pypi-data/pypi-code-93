from setuptools import setup, find_packages
from os import path

VERSION = '0.1.3'
DESCRIPTION = 'Generic code for processing and execution for OMD EMEA'
LONG_DESCRIPTION = 'This package houses generic code and processed for OMD EMEA. The purpose of this package is to make it super easy to download the code using Pip instead of cloning the relevant GitLab project and branch.'

# read the contents of your README file
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory+'/omd_emea', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Setting up
setup(
    name="omd_emea",
    version=VERSION,
    author="Aniruddha Sengupta",
    author_email="aniruddha.sengupta@omd.com",
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['requests',
                      'pandas',
                      'facebook-business',
                      'google',
                      'google-api-python-client',
                      'google-cloud',
                      'google-cloud-storage',
                      'google-cloud-bigquery-storage',
                      'sqlalchemy',
                      'selenium'],
    keywords=['python', 'omd', 'general', 'generic'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)