import setuptools

with open("README.txt", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="KevinSR",
    version="0.1.18",
    author="Kevin Zhang",
    author_email="zhangkuanmayo@gmail.com",
    description="This package includes inference codes supporting Super-resolution image and mask interpolations.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/KevinSR",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pydicom>=2.1.2",
        "numpy>=1.18.5",
        "matplotlib>=3.4.2",
        "scipy>=1.4.1",
        "tensorflow-gpu>=2.3.0",
        "pillow>=8.0.0",
    ],
    python_requires='>=3.6',
)
