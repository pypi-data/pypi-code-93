from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Zero_ILumi_Calculadora_Package",
    version="0.0.1",
    author="Zero ILumi",
    author_email="zeroilumi666@gmail.com",
    description="Uma Calculadora Desenvolvida por Zero_ILumi",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZeroILumi",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)