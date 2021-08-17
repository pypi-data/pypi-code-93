import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="airflow_file_to_bq",
    version="0.1.3",
    author="Florian Pribahsnik",
    author_email="florian@pribahsnik.com",
    license="MIT",
    description="Specialized Airflow operators for moving files from a GCS-bucket to Landing-Zone, Staging-Zone and Production-Zone in BigQuery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=[
        "apache-airflow>=2.0",
        "pandas>=1.0",
        "smart_open[gcs]>=4.0",
        "google-cloud-bigquery>=2.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
