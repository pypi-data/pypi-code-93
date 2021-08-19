import setuptools
import re

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

version = ''
with open('src/iepy/__init__.py') as f:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
        f.read(),
        re.MULTILINE
    ).group(1)

if not version:
    raise RuntimeError('version is not set')

setuptools.setup(
    name="b23iepy",  # Replace with your own username
    version=version,
    author="Bertik23",
    author_email="bertikxxiii@gmail.com",
    description="Package for Hydrocarbon to Image conversion",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bertik23/iepy",
    packages=setuptools.find_packages(where="src"),
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    package_dir={"": "src"},
    package_data={'iepy': ['data.json']}
)
