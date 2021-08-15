import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sqlalchemy_sqlite_session",
    version="0.2.0",
    author="WangJulong",
    author_email="496349619@qq.com",
    description="get sqlite session or engine for sqlalchemy",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/tensorflows/sqlalchemy-sqlite-session",
    project_urls={
        "project url": "https://gitee.com/tensorflows/sqlalchemy-sqlite-session",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)