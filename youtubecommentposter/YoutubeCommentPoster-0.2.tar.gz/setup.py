from setuptools import setup, find_packages
import codecs
import os
import pip
from pip._internal.req import parse_requirements
import io
# try:
#     import pypandoc
#     long_description = pypandoc.convert('README.md', 'rst')
#     long_description = long_description.replace("\r","") # Do not forget this line
# except OSError:
#     print("Pandoc not found. Long_description conversion failure.")
#     import io
    # pandoc is not installed, fallback to using raw contents
with open('README.md') as f:
     long_description = f.read()
install_reqs = parse_requirements('requirements.txt',session=False)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.requirement) for ir in install_reqs]
VERSION = '0.2'
DESCRIPTION ="A wrapper to comment on videos via your account!"
LONG_DESCRIPTION = 'A wrapper that allows you to comment on someone video with your script usefull for bots :)'

# Setting up
setup(
    name="YoutubeCommentPoster",
    version=VERSION,
    author="KeinShin",
    author_email="<ytcomments@ytcomments.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=['ytcomment'],
    install_requires=reqs,
    keywords=['python', 'youtube', 'scraper', 'youtube', 'comments', 'commentyoutubevideo'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)