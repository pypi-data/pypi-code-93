from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="Zero_ILumi_Calculadora_Package",
    version="0.0.2",
    author="Zero ILumi",
    author_email="zeroilumi666@gmail.com",
    description="Uma Calculadora Desenvolvida por Zero_ILumi",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZeroILumi/Projetos_de_Teste_ver_0.0.1/tree/master/Testes_Complexos/Pacotes%20Python/Zero_ILumi_Pacote_Teste",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)