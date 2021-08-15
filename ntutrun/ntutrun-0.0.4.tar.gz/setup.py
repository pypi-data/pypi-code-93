import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    'GitPython>=3.0.8'
]

setuptools.setup(
    name="ntutrun", # Replace with your own username
    version="0.0.4",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires
)