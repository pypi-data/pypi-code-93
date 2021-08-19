import setuptools

setuptools.setup(
    name="ptgcalls-wrapper",
    version="1.1.0",
    author="Shohih Abdul",
    author_email="shohih242@gmail.com",
    description="A library to use the PyTgCalls easier.",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["youtube-dl", "py-tgcalls", "asyncio"],
)
