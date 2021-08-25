from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name = 'psypher',
    version = '1.0.0',
    author = 'origamizyt',
    author_email = 'zhaoyitong18@163.com',
    description = 'A modern asymmetric encryption scheme.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://gitee.com/origamizyt/psypher',
    packages = ['psypher'],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires = ">=3.6",
    install_requires = ['cryptography']
)