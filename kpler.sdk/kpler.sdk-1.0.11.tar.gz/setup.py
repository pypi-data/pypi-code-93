from setuptools import find_namespace_packages, setup


with open("README.md") as fh:
    long_description = fh.read()

setup(
    name="kpler.sdk",
    description="A Python wrapper around the Kpler client API",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://github.com/kpler/python-sdk",
    author="Kpler",
    author_email="engineering@kpler.com",
    license="Apache License, Version 2.0",
    packages=find_namespace_packages(
        where="src",
        include=["kpler*"],
    ),
    package_dir={"": "src"},
    install_requires=[
        "pandas>=1.0.0,<=1.3.0",
        "requests>=2.20.0",
    ],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "doc": [
            "Sphinx==3.2.1",
            "sphinx_rtd_theme==0.5.0",
            "sphinx-autodoc-typehints==1.6.0",
        ],
        "test": [
            "black==18.9b0",
            "mypy-extensions==0.4.3",
            "mypy==0.782",
            "pre-commit==2.6.0",
            "pytest==5.0.0",
            "python-dateutil==2.8.1",
            "pytest-rerunfailures==9.1.1",
        ],
        "publish": [
            "twine==3.2.0",
        ],
    },
)
