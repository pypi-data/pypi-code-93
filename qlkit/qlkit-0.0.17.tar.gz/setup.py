import setuptools
import os
import io


DESCRIPTION = "Python application development toolkit"

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        long_description = '\n' + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

setuptools.setup(
    name="qlkit",
    version="0.0.17",
    author="qianlu",
    author_email="tech001@qianlu.com",
    description=DESCRIPTION,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["sqlalchemy", "protobuf", "grpcio"],
    extras_require={},
    python_requires='>=3.8',
)
