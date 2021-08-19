import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

install_requires = [
    'anytree==2.8.0',
]

dev_requires = [
    'build==0.5.1',
    'twine>=3.4.2,<4',
    'pip-tools>=5,<6',
    'pytest>=6.2.4,<6.3',
]

setuptools.setup(
    name="proto-formatter",
    version="0.0.3",
    author="YiXiaoCuoHuaiFenZi(一小撮坏分子)",
    author_email="249664317@qq.com",
    description="Protocol Buffers file formatter.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YiXiaoCuoHuaiFenZi/proto-formatter",
    project_urls={
        "Bug Tracker": "https://github.com/YiXiaoCuoHuaiFenZi/proto-formatter/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=install_requires,
    setup_requires=[],
    tests_require=[],
    extras_require={
        "dev": dev_requires
    },
)
