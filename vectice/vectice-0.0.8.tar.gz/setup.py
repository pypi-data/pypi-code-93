import sys

if sys.version_info < (3, 7):
    print("vectice requires Python 3 version >= 3.7.", file=sys.stderr)
    sys.exit(1)

import io
import os
from setuptools import setup

package_root = os.path.abspath(os.path.dirname(__file__))

readme_filename = os.path.join(package_root, "README.rst")

with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

setup(
    name="vectice",
    version="0.0.8",
    description="Vectice Python library",
    long_description=readme,
    author="Vectice Inc.",
    author_email="sdk@vectice.com",
    url="https://github.com/vectice/vectice-python",
    packages=["vectice", "vectice.api", "vectice.api.output", "vectice.adapter", "vectice.entity", "vectice.models"],
    license="Apache License 2.0",
    keywords=["Vectice", "Client", "API", "Adapter"],
    platforms=["Linux", "MacOS X", "Windows"],
    python_requires=">=3.7.1",
    install_requires=[
        "requests >= 2.5.0",
        "python-dotenv >= 0.10.0",
        "GitPython",
        "PyGithub",
    ],
    tests_require=["mock >= 1.0.1", "pytest", "coverage", "pytest-cov", "testcontainers"],
    extras_require={
        "dev": ["bandit", "black", "flake8", "mypy", "pre-commit", "Pygments"],
        "mlflow": ["mlflow"],
        "doc": ["sphinx", "recommonmark", "nbsphinx", "sphinx-rtd-theme", "pypandoc", "jupyterlab"],
    },
    classifiers=[
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Typing :: Typed",
    ],
)
