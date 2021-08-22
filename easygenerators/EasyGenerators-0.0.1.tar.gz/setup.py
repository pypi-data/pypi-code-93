import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EasyGenerators",
    version="0.0.1",
    author="Haider Ali",
    author_email="ali075398@example.com",
    description="A powerful package of python generators",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ProjectsWithPython/EasyGenerators",
    project_urls={
        "Bug Tracker": "https://github.com/ProjectsWithPython/EasyGenerators/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)