import sys

from setuptools import setup

about = {}
with open("selfcaffeinate/__about__.py") as fp:
    exec(fp.read(), about)

with open("README.md", "r") as fp:
    long_description = fp.read()


def check_platform():
    if sys.platform != 'darwin':
        raise SystemExit("ERROR: requires macOS to install or build.")
    return ''


setup(name=about["__title__"],
      version=about["__version__"],
      platforms=['darwin'],
      description=about["__summary__"],
      long_description=long_description,
      long_description_content_type="text/markdown",
      author="Zachary Cutlip",
      author_email="uid000@gmail.com",
      url="https://github.com/zcutlip/py-self-caffeinate",
      license="MIT",
      packages=['selfcaffeinate'],
      python_requires='>=3.7',
      install_requires=[check_platform()],
      package_data={'selfcaffeinate': ['config/*']},
      )
