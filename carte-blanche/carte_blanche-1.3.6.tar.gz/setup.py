from setuptools import setup, find_packages


packages = find_packages(exclude=['tests'])

print('packages')
print(packages)

setup(
    name='carte_blanche',

    version='1.3.6',

    url='https://github.com/huffmsa/carte-blanche-python-utils',

    license='MIT',

    author='Sam Huffman',

    author_email='huffmsa@gmail.com',

    description='Collection of commonly used utilities at the Carte Blanche companies',

    packages=find_packages(exclude=['tests']),

    long_description=open('README.md').read(),

    zip_safe=False,

    setup_requires=[
        "atomicwrites>=1.4.0",
        "attrs>=21.2.0",
        "coloredlogs>=15.0.1",
        "humanfriendly>=9.2",
        "jsonschema>=2.6.0",
        "more-itertools>=4.3.0",
        "pluggy>=0.7.1",
        "py>=1.5.4",
        "pytest>=3.7.2",
        "six>=1.14.0",
        "flake8>=3.7.9",
        "mccabe>=0.6.1",
        "pycodestyle>=2.5.0"
    ],

    install_requires=[
        "astroid==2.5",
        "atomicwrites==1.4.0",
        "attrs==21.2.0",
        "bleach==4.0.0",
        "certifi==2021.5.30",
        "cffi==1.14.6",
        "charset-normalizer==2.0.4",
        "colorama==0.4.4",
        "coloredlogs==15.0.1",
        "cryptography==3.4.7",
        "docutils==0.17.1",
        "entrypoints==0.3",
        "falcon==2.0.0",
        "flake8==3.7.9",
        "humanfriendly==9.2",
        "idna==3.2",
        "importlib-metadata==4.6.4",
        "isort==4.3.21",
        "jeepney==0.7.1",
        "jsonschema==2.6.0",
        "keyring==23.1.0",
        "lazy-object-proxy==1.4.3",
        "mccabe==0.6.1",
        "more-itertools==4.3.0",
        "packaging==21.0",
        "pkginfo==1.7.1",
        "pluggy==0.7.1",
        "psycopg2==2.8.4",
        "psycopg2-binary==2.9.1",
        "py==1.5.4",
        "pycodestyle==2.5.0",
        "pycparser==2.20",
        "pyflakes==2.1.1",
        "Pygments==2.10.0",
        "pylint==2.5.3",
        "pymongo==3.10.1",
        "pyparsing==2.4.7",
        "pytest==3.7.2",
        "readme-renderer==29.0",
        "redis==3.4.1",
        "requests==2.26.0",
        "requests-toolbelt==0.9.1",
        "rfc3986==1.5.0",
        "SecretStorage==3.3.1",
        "six==1.14.0",
        "SQLAlchemy==1.3.15",
        "toml==0.10.1",
        "tqdm==4.62.1",
        "twine==3.4.2",
        "urllib3==1.26.6",
        "webencodings==0.5.1",
        "wrapt==1.11.2",
        "zipp==3.5.0",

    ],

    test_suite=''
)
