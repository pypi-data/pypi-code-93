import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cuwais-common",
    version="1.3.1",
    author="Joe O'Connor",
    author_email="jo429@cam.ac.uk",
    description="The shared libraries for CUWAIS competitions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AI-Wars-Soc/common",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'sqlalchemy~=1.4.23',
        'pyyaml~=5.4.1',
        'psycopg2~=2.9.1',
        'chess~=1.6.1'
    ],
    python_requires='>=3.6',
)
