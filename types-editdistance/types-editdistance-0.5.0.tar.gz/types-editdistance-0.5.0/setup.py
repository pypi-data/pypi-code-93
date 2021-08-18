from setuptools import setup

name = "types-editdistance"
description = "Typing stubs for editdistance"
long_description = '''
## Typing stubs for editdistance

This is a PEP 561 type stub package for the `editdistance` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `editdistance`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/editdistance. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `bfff7d763bd216a479f4babcc19ff677bf198de4`.
'''.lstrip()

setup(name=name,
      version="0.5.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['editdistance-stubs'],
      package_data={'editdistance-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Typed",
      ]
)
