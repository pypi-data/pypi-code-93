from __future__ import unicode_literals

from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


def version():
    with open('anna/VERSION') as f:
        return f.read()

setup(
    name='anna',
    version=version(),
    description='A Neat configuratioN Auxiliary',
    long_description=readme(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development',
    ],
    keywords='configuration framework',
    url='https://gitlab.com/Dominik1123/Anna',
    author='Dominik Vilsmeier',
    author_email='dominik.vilsmeier1123@gmail.com',
    license='BSD-3-Clause',
    packages=[
        'anna',
        'anna.frontends',
        'anna.frontends.qt',
        'anna.unittests',
    ],
    install_requires=[
        'docutils',
        'numpy',
        'scipy',
        'six',
    ],
    include_package_data=True,
    zip_safe=False
)
