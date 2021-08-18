from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'ASG Utils contains my main standard Python Librairies + some extra helpers functions'
LONG_DESCRIPTION = 'This lib contains rudimentary packages + some extra custom helpers functions.'

# Setting up
setup(
    name="asgutils",
    version=VERSION,
    author="Alexandre Suire",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    # install_requires=['NOM_DES_LIBRAIRIES_A_INSTALLER'],
    install_requires=[
        'arrow', 'pandas', 'requests', 'SQLAlchemy', 'psycopg2', 'pymsteams', 'google-api-python-client',
        'google-auth-httplib2', 'google-auth-oauthlib'
    ],
    keywords=['python', 'utils', 'helpers'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ])
