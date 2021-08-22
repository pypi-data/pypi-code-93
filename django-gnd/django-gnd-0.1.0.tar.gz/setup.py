import setuptools
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name='django-gnd',
    version='0.1.0',
    description="""A django package to query and store data from Lobid's GND-API""",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Peter Andorfer',
    author_email='peter.andorfer@oeaw.ac.at',
    url='https://github.com/acdh-oeaw/django-gnd',
    packages=[
        'gnd',
    ],
    include_package_data=True,
    install_requires=[
        'Django>=3.1',
        'pylobid>=1.3.1',
        'python-dateutil>=2.8'
    ],
    license="MIT",
    zip_safe=False,
    keywords='django-gnd'
)
