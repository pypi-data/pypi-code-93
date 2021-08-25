import pathlib
from setuptools import setup, find_packages
import os

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.4'
PACKAGE_NAME = 'facef'
AUTHOR = 'Duy Nguyen Manh'
AUTHOR_EMAIL = 'manhduy160396@email.com'
URL = 'https://github.com/DuyKK/duyai'

LICENSE = 'MIT License'
DESCRIPTION = 'face recognition library, flexible and easy to use'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'opencv-python',
      'gdown'
]

cache_dir = os.path.join(os.path.expanduser('~'), '.duyai')
if os.path.exists(cache_dir) == False:
    os.mkdir(cache_dir)

model_dir = os.path.join(os.path.expanduser('~'), '.duyai/model')
if os.path.exists(model_dir) == False:
    os.mkdir(model_dir)

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )
