import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="l0n0lnat",
    version="2.3.4",
    author="l0n0l",
    author_email="1038352856@qq.com",
    description="内网穿透服务器，客户端",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/l00n00l/l0n0lnat",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    include_package_data=True,
    package_data={
        "": ["*.so"]
    },
    install_requires=[
        "pymonocypher"
    ],
    entry_points={
        "console_scripts": [
            "l0n0lnatserver = l0n0lnat.Commands:run_reverse_server",
            "l0n0lnatclient = l0n0lnat.Commands:run_reverse_client",
        ]
    }
)
