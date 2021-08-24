import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("superwise/requirements.txt", "r") as f:
    requirements = [x.strip() for x in f.readlines()]

setuptools.setup(
    name="superwise",
    version="2.0.17",
    description="Superwise SDK",
    url="https://dash.readme.com/project/superwise/v2.0/docs/getting-started",
    author="Superwise.ai",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email="tech@superwise.com",
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(exclude=["tests"]),
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3",
    setup_requires=[requirements],
    install_requires=[requirements],
)
