from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
      name='pyXhCustApp',
      version='0.0.3',
      description='Custom App Environment',
      py_modules=['pyXhCustApp'],
      package_dir={'':'src'},
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/xh-dev-py/pyXhCustApp",
      author="xethhung",
      author_email="pypi@xethh.dev",
      extras_require = {
        "dev": [
            "pytest>=3.7",
        ]
      }
)