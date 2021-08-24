import os
from setuptools import setup

dir_ = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(dir_, 'README.md'), 'r') as rm:
    README = rm.read()

setup(name='live-pandoc',
      version='0.1.1',
      description='A program for live rendering a pandoc command',
      long_description=README,
      long_description_content_type="text/markdown",
      url='http://github.com/blockjoe/live-pandoc',
      author='blockjoe',
      author_email='blockjoe46@gmail.com',
      license='MIT',
      classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
      ],
      packages=('live_pandoc',),
      install_requires=('watchdog',),
      include_package_data=True,
      entry_points={
          'console_scripts': ['live-pandoc=live_pandoc.main:main']
      }
)
