import setuptools


setuptools.setup(
    name="AsyncThread",
    version="0.0.1",
    author="Geographs",
    author_email="87452561+Geographs@users.noreply.github.com",
    description="A threading implementation for asynchronous functions.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Geographs/AsyncThread",
    project_urls={
        "GitHub": "https://github.com/Geographs/AsyncThread",
        "Bug Tracker": "https://github.com/Geographs/AsyncThread/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.6",
)
