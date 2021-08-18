
import pathlib
import setuptools
from peach_collector import __version__, __title__, __description__

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setuptools.setup(
    name=__title__,
    version=__version__,
    url="https://git.ebu.io/now/peach-collector-py",
    author="Matti Kotsalainen",
    author_email="kotsalainen@ebu.ch",
    description=__description__,
    long_description=README,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=(
        "aioredis",
        "aioredlock",
        "httpx",
        "orjson",
    ),
)
