import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wenbot",
    version="0.0.8",
    author="Wenbo Zhao",
    author_email="zhaowb@gmail.com",
    description="Simple bot wrapper of selenium basic functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhaowb/wenbot.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['selenium'],
    py_modules=['wenbot']
)
