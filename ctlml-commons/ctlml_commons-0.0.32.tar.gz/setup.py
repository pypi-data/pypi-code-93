from setuptools import find_packages, setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="ctlml_commons",
    version="0.0.32",
    description="CTLML Trader Commons",
    url="https://github.com/mhowell234/ctlml_commons",
    author="mhowell234",
    author_email="mhowell234@gmail.com",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(include=["ctlml_commons", "ctlml_commons.*"]),
    python_requires=">=3.10, <4",
)

