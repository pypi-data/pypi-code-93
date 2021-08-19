import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open('requirements.txt','r') as fr:
    requires = fr.read().split('\n')

setuptools.setup(
    # pip3 salehoo free trial
    name="salehoo free trial", 
    version="1",
    author="salehoo free trial",
    author_email="admin1@salehoo.com",
    description="salehoo free trial",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://a41fcvk9gr764d4mfks5-8cu5i.hop.clickbank.net/?tid=PYFI",
    project_urls={
        "Bug Tracker": "https://github.com/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=requires,
)
