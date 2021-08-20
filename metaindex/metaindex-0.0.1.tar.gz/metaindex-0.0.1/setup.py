import setuptools


with open('README.md', encoding='utf-8') as fd:
    long_description = fd.read()


with open('LICENSE', encoding='utf-8') as fd:
    licensetext = fd.read()


setuptools.setup(
    name='metaindex',
    version='0.0.1',
    description="Utility to tag files",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license_file="LICENSE",
    license_files="LICENSE",
    url="https://github.com/vonshednob/metaindex",
    author="R",
    author_email="devel+doctag@kakaomilchkuh.de",
    entry_points={},
    packages=[],
    package_data={},
    data_files=[],
    install_requires=[],
    extras_require={},
    python_requires='>=3.0',
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Console',
                 'Environment :: Console :: Curses',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3',
                 'Topic :: Text Processing :: Indexing',])

