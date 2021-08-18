from setuptools import setup, find_packages
from fcg.version import __version__

setup(
    name='fcg',
    version=__version__,
    author='charon.',
    author_email='mzrwalzy@163.com',
    description='fastapi code generator',
    long_description='README.md',
    url='https://github.com/mzrwalzy/fcg.git',
    packages=find_packages(),
    install_requires=[
            'docopt==0.6.2',
        ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': [
            'fcg = fcg.__main__:main'
        ]
    },
    zip_safe=False,
)
