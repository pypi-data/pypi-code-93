import setuptools

setuptools.setup(
    name="graiax-v4-dependency",
    version="1.0.1",
    author="purofle",
    author_email="3272912942@qq.com",
    description="graia v4 版本的所有依赖",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.8<4.0',
    install_requires="""graia-application-mirai==0.19.2
    graia-broadcast==0.8.11
    graia-scheduler==0.0.4
    graia-saya==0.0.9
    graia-component-selector==0.0.6
    graia-template==0.0.4"""
)
