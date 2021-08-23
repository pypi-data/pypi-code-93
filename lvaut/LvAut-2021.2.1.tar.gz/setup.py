import setuptools

with open("README.rst", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="LvAut", # Replace with your own username
    version="2021.2.1",
    author="lorry_rui",
    author_email="lrui@logitech.com",
    description="Audio sound file testing/analyzes module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lorrytoolcenter/LvAut",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
