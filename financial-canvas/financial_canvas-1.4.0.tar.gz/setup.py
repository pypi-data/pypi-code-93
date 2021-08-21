import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

setuptools.setup(
    name="financial_canvas",
    version="1.4.0",
    author="Evgeniia Vakarina",
    author_email="27793901+EvgeniiaVak@users.noreply.github.com",
    description="Draw interactive candlesticks on browser canvas from Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=requirements,
)