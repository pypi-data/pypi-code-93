# coding: utf-8
"""Setup script for IVA TPU."""
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='iva-tpu',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      version="11.0.17",
      author="Maxim Moroz",
      author_email="m.moroz@iva-tech.ru",
      description="IVA TPU Python API",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="http://git.mmp.iva-tech.ru/tpu_sw/iva_tpu_sdk",
      install_requires=[
            'numpy>=1.14',
      ],
      zip_safe=False,
      python_requires='>=3.6',
      )
