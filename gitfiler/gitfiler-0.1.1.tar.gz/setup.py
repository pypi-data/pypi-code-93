from setuptools import find_packages, setup

source_url = "https://github.com/samedamci/gitfiler"

setup(
    name="gitfiler",
    version="0.1.1",
    description="Simple tool to download single file from GitHub or GitLab.",
    author="samedamci",
    author_email="samedamci@disroot.org",
    url=source_url,
    project_urls={"Source": source_url, "Tracker": f"{source_url}/issues"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries",
        "Typing :: Typed",
    ],
    keywords="github gitlab downloader",
    python_requires=">=3.6,<4.0",
    packages=find_packages(include=["gitfiler"]),
)
