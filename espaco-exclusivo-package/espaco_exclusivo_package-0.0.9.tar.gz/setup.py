import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="espaco_exclusivo_package",
    version="0.0.9",
    author="Diego Isaac Haruwo Yosiura",
    author_email="diego@ampereconsultoria.com.br",
    description="Pacote de métodos usados para implementação da API de acesso aos produtos Ampere Consultoria",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/diego.yosiura.ampere/espaco-exclusivo-package.git",
    project_urls={
        "Bug Tracker": "https://gitlab.com/diego.yosiura.ampere/espaco-exclusivo-package/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    scripts=[],
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['requests', 'requests-toolbelt']
)
