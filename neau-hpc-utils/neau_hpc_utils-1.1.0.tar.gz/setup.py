import setuptools

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="neau_hpc_utils",
    version="1.1.0",
    author="yuquanfeng",
    author_email="hannerduffly@gmail.com",
    description="The utils from NEAU HPC Group",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yuquanF/neau_hpc_utils",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)