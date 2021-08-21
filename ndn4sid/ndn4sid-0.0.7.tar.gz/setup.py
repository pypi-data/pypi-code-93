from setuptools import setup


with open('README.md','r') as fh:
    long_description = fh.read()

setup(
    name='ndn4sid',
    version='0.0.7',
    description='A package to perform n4sid on nD systems',
    py_modules=['linearalgebra','misc','constants','systems'],
    package_dir={'':'src'},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    install_requires = [
        'numpy ~= 1.19',
        ],
    extras_require = {
        'dev':[
            'pytest ~=3.7',
            'check-manifest ~=0.46',
            'twine ~=3.4.2',
            'tox ~=3.24',
        ],
    },
    author = 'Bob Vergauwen',
    author_email = 'bob.vergauwen@gmail.com',
    url = 'https://example.com'
)