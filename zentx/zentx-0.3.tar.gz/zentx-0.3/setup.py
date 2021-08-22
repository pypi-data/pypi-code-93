from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.3"
DESCRIPTION = 'ENCRYPTION METHODS'
LONG_DESCRIPTION = 'ZENTX'

# Setting up
setup(
    name="zentx",
    version=VERSION,
    author="K.A.ISHAN OSHADA",
    author_email="<ic31908@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    keywords=['lex','pix_file','m_compile','dict_zip'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
  
    ]
)
