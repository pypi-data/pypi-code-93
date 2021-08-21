from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Framework :: AsyncIO",
]

project_urls = {
    "Bug Tracker": "https://github.com/33TU/fstream/issues",
}

setup(
    name="fstream",
    version='0.0.3',
    description="Faster async streams for Python.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=classifiers,
    project_urls=project_urls,
    url="https://github.com/33TU/fstream",
    license="MIT",
    packages=find_packages(exclude=["examples"]),
    install_requires=[],
    extras_require={},
    python_requires=">=3.5",
    include_package_data=True,
)
