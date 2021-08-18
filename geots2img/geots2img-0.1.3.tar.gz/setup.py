from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name="geots2img",
      version="0.1.3",
      description="Geo Time Series to Image",
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/juliandehoog/geo-timeseries-to-image",
      author="Julian de Hoog",
      author_email='julian@dehoog.ca',
      license="MIT",
      packages=find_packages(),
      install_requires=[
            'pandas',
            'setuptools',
            'numpy',
            'matplotlib',
            'scipy',
            'Pillow',
            'pytz',
      ],
      zip_safe=False)
