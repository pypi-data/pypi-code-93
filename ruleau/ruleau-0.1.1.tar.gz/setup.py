import re
from pathlib import Path
import itertools

import setuptools

with open("ruleau/__init__.py", "r") as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE
    ).group(1)

with open(Path(__file__).parent / "README.md", encoding='utf-8') as f:
    long_description = f.read()

with open("./requirements.txt", "r") as r:
    requirements = r.readlines()

setuptools.setup(
    name="ruleau",
    version=version,
    author="Unai Ltd",
    author_email="pypi@unai.com",
    description="A python rules engine",
    long_description=long_description,
    long_description_content_type="text/markdown",
    tests_require=["pytest"],
    url="https://github.com/unai/ruleau",
    packages=setuptools.find_packages(exclude=("tests",)),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6.14",
    entry_points={"console_scripts": ["ruleau-docs=ruleau.docs:main"]},
    package_data={"": ["html/documentation.html"]},
    include_package_data=True,
    install_requires=requirements,
)
