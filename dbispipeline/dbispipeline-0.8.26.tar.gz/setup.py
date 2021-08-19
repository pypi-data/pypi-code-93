"""dbispipeline python packages."""
from setuptools import find_packages
from setuptools import setup

# we should not use the requirements.txt at this point after all.
# https://packaging.python.org/discussions/install-requires-vs-requirements
# /#requirements-files

with open('README.md') as fh:
    long_description = fh.read()

setup(
    name='dbispipeline',
    version='0.8.26',
    author='Benjamin Murauer, Michael Vötter',
    author_email='b.murauer@posteo.de',
    description='should make things more reproducible',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://git.uibk.ac.at/dbis/software/dbispipeline',
    install_requires=[
        'gitpython>2',
        'matplotlib',
        'pandas',
        'psycopg2-binary',
        'scikit-learn',
        'sqlalchemy>1.3',
        'click',
        'logzero',
        'pyyaml',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Topic :: Scientific/Engineering',
    ],
    entry_points={
        'console_scripts': [
            'dp=dbispipeline.cli.main:main',
            'dbispipeline=dbispipeline.cli.main:main',
            'dbispipeline-link=dbispipeline.cli.main:link',
        ],
    },
    python_requires='>=3.6',
    include_package_data=True,
    setup_requires=[],
    test_suite='tests',
    tests_require=[],
    packages=find_packages('src'),
    package_dir={'': 'src'},
)
