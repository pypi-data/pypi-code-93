from pathlib import Path
from setuptools import setup
from setuptools import find_packages

PROJECT = "redex"
REPOSITORY = f"manifest/{PROJECT}"
README = (Path(__file__).parent / "README.md").read_text()

# Setup project version.
__version__ = None
with open(f"src/{PROJECT}/version.py") as file:
    exec(file.read(), globals())

# Setup keywords.
# https://setuptools.readthedocs.io/en/latest/references/keywords.html
setup(
    name=PROJECT,
    version=__version__,
    author="Andrei Nesterov",
    author_email="ae.nesterov@gmail.com",
    url=f"https://github.com/{REPOSITORY}",
    description="A combinator library for designing algorithms",
    long_description=README,
    long_description_content_type="text/markdown",
    project_urls={
        "Documentation": f"https://{PROJECT}.readthedocs.io",
        "Source Code": f"https://github.com/{REPOSITORY}",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
        "Typing :: Typed",
    ],
    # Required for mypy to find the installed package.
    zip_safe=False,
    package_data={f"src/{PROJECT}": ["py.typed"]},
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
    ],
    extras_require={
        "docs": ["sphinx", "furo", "nbsphinx", "ipykernel"],
        "development": ["hypothesis", "pylint"],
    },
)
