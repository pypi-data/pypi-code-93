import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="KNMIdata",
    version="1.0.2",
    author="Ugurcan Akpulat",
    author_email="ugurcan.akpulat@gmail.com",
    description="KNMI hourly data API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/macukadam/KNMI_weather_api",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)