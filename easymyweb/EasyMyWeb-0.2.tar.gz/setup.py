import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="EasyMyWeb",
    version="0.2",
    author="Sheng Fan",
    author_email="1175882937@qq.com",
    description="deploy your website quickly",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.ft2.club/fred913/easymyweb",
    packages=setuptools.find_packages(),
    install_requires=['flask', 'uvicorn', 'requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
