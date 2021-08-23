# coding:utf-8

from setuptools import setup

setup(
    name="knitkit-mill",
    url='https://github.com/colin4124',
    packages=["knitkit_mill"],
    package_data={
        "knitkit_mill": [
            "assets/mill",
            "assets/cache.tar.gz",
        ],
    },
    use_scm_version={"relative_to": __file__, "write_to": "knitkit_mill/version.py",},
    author="Leway Colin",
    author_email="colin4124@gmail.com",
    description=(
        "Mill Binary and Cache is a fat JAR with all of its dependencies."
    ),
    license="Apache-2.0 License",
    keywords=[
        "mill",
    ],
    setup_requires=["setuptools_scm",],
    install_requires=[
    ],
    # Supported Python versions: 3.6+
    python_requires=">=3.6",
)
