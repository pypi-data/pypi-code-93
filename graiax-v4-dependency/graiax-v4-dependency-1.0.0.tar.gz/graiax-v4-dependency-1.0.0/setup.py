import setuptools

with open("requirements.txt", "r") as f:
    install_requires = f.read()

setuptools.setup(
    name="graiax-v4-dependency",
    version="1.0.0",
    author="purofle",
    author_email="3272912942@qq.com",
    description="graia v4 版本的所有依赖",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8<4.0',
    install_requires=install_requires
)
