import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='gpke_calendar',
    version='0.7.5',
    packages=find_packages('.', exclude=['env']),
    include_package_data=True,
    license='BSD License',
    description='gpke calendar',
    long_description=README,
    author='Raymond Schmidt',
    url='https://kingmray@bitbucket.org/kingmray/gpke-calendar.git',
    install_requires=[
        'workdays',
      ],
    classifiers=[],
)
