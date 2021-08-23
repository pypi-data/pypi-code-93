__version__ = "1.2.2"

from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
    long_description = f.read()


if __name__ == '__main__':
    setup(
        name='dblogging',
        packages=find_packages(where='.', exclude=['examples']),
        package_dir={
            'dblogging': 'dblogging'
        },
        include_package_data=True,
        description='Persist logs With SQLite. Easy to query logs.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        version=__version__,
        author='Tyler Spens',
        author_email='mrtspens@gmail.com',
        keywords=['logging', 'persistent', 'database', 'db', 'sqlite', 'log', 'persist', 'data'],
        install_requires=[
            'jsonpickle',
            'Pygments',
            'htmlmin',
            'simplejson'
        ],
        url='https://gitlab.com/tspens/dblogging',
        download_url='https://gitlab.com/tspens/dblogging/-/archive/V1.0.2/dblogging-V1.0.2.zip',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.8',
        ]
    )
