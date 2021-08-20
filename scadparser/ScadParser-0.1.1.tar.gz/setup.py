from setuptools import setup
import io
import re
from os.path import dirname
from os.path import join

def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()

setup(
    name='ScadParser',
    description='Parse code files from OpenSCAD',
    long_description=re.compile(
        '^.. start-badges.*^.. end-badges',
        re.M | re.S
    ).sub(
        '',
        read('README.rst')
    ),
    long_description_content_type='text/x-rst',
    author='Roie R. Black',
    author_email='roie.black@gmail.com',
    url='https://github.com/rblack42/math-magik',
    license='BSD',
    version='0.1.1',
    packages=['scadparser'],
entry_points= {
        "console_scripts": [
            "scadparser = scadparser.cli:cli"
        ]
    },
    python_requires='>=3.8, <3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: tox',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Testing',
    ],
)
