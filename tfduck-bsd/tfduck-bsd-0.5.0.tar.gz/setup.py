import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tfduck-bsd",
    version="0.5.0",
    author="yuanxiao",
    author_email="yuan6785@163.com",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    # 需要安装的依赖
    install_requires=[
         'requests>=2.20.0',
         'django==2.2.12',
         'oss2==2.5.0',
         'ThinkingDataSdk==1.1.14',
         'kubernetes==12.0.1'
    ],
    python_requires=">=3.5",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    scripts=['bin/tfduck'],
)
