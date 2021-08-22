import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SentinelOne4py",
    version="0.0.2",
    author="Shahar Margalit",
    author_email="shaharma@gmail.com",
    description="SentinelOne Api for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sshahar/sentinelone4py",
    project_urls={
        "Bug Tracker": "https://github.com/sshahar/sentinelone4py/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)
