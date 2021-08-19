from setuptools import setup, find_packages


packages = find_packages(exclude=['tests'])

print('packages')
print(packages)

setup(
    name='carte_blanche',

    version='1.3.8',

    url='https://github.com/huffmsa/carte-blanche-python-utils',

    license='MIT',

    author='Sam Huffman',

    author_email='huffmsa@gmail.com',

    description='A package of web server development libraries',

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
        "cffi==1.14.6",
        "coloredlogs==15.0.1",
        "cryptography==3.4.7",
        "entrypoints==0.3",
        "falcon==2.0.0",
        "flake8==3.7.9",
        "humanfriendly==9.2",
        "isort==4.3.21",
        "jeepney==0.7.1",
        "jsonschema==2.6.0",
        "lazy-object-proxy==1.4.3",
        "mccabe==0.6.1",
        "more-itertools==4.3.0",
        "pip-autoremove==0.9.1",
        "pluggy==0.7.1",
        "psycopg2-binary==2.9.1",
        "py==1.10.0",
        "pycodestyle==2.5.0",
        "pycparser==2.20",
        "pyflakes==2.1.1",
        "pylint==2.5.3",
        "pymongo==3.10.1",
        "pytest==3.7.2",
        "redis==3.4.1",
        "SecretStorage==3.3.1",
        "six==1.14.0",
        "SQLAlchemy==1.3.15",
        "toml==0.10.1",
        "wrapt==1.11.2"
    ],

    test_suite=''
)
