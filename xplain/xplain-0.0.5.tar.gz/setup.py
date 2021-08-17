import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="xplain", # Replace with your own username
    version="0.0.5",
    author="Xplain Data",
    author_email="peide.wang@xplain-data.com",
    description="A xplain python package",
    long_description="A python package to access xplain data analytics",
    long_description_content_type="text/markdown",
    url="https://xplain-data.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas',
         'requests',
        'treelib'],
    python_requires='>=3.6',
)