from setuptools import setup, find_packages


def read_version(module_name):
    from re import match, S
    from os.path import join, dirname

    with open(join(dirname(__file__), module_name, "__init__.py")) as f:
        return match(r".*__version__.*('|\")(.*?)('|\")", f.read(), S).group(2)


setup(
    name="cytra",
    version=read_version("cytra"),
    keywords="database",
    packages=find_packages(),
    install_requires=[
        "gongish >= 0.5.0",
        "sqlalchemy >= 1.4.0",
        "pytz >= 2021.1",
        "ujson >= 4.0.0",
        "PyJWT >= 2.1.0",
        "redis >= 3.5.3",
        "user-agents >= 2.2.0",
        "webtest >= 2.0.35",
    ],
)
