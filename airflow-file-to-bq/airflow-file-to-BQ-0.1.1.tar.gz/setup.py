import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()


setuptools.setup(
    name="airflow-file-to-BQ",
    version="0.1.1",
    author="Florian Pribahsnik",
    author_email="florian@pribahsnik.com",
    license="MIT",
    description="Specialized Airflow operators for moving files from a GCS-bucket to Landing-Zone, Staging-Zone and Production-Zone in BigQuery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=[req for req in requirements if req[:2] != "# "],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
