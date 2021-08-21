from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='pycftools',
      version='0.2.8',
      description='This library provides access to all cftools api methods. It is a kind of wrapper for all methods.',
      url='https://github.com/Exordio/pycftools',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Ivan Golubev',
      author_email='wecatorz@gmail.com',
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      py_modules=['pycftools'],
      install_requires=[
          'requests>=2.26.0',
      ],
      zip_safe=False)
