import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pmb_py",
    version="0.1.8",
    author="Noflame.lin",
    author_email="linjuang@gmail.com",
    description="pmb restful api python wrap",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MoonShineVFX/pmb_py_api",
    install_requires=['requests', 'simplejson'],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)