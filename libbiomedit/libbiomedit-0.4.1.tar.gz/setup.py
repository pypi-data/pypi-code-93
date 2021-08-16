#!/usr/bin/env python3

from datetime import datetime
from setuptools import setup, find_packages

# 0.0.0-dev.* version identifiers for development only (not public)
__version__ = "0.0.0.dev" + datetime.now().strftime("%Y%m%d")

if __name__ == "__main__":
    setup(
        name="libbiomedit",
        version="0.4.1",
        license="LGPL3",
        description="Shared library for arround biomedit data transfer",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        author="Robin Engler, "
        "Jarosław Surkont, "
        "Riccardo Muri, "
        "Gerhard Bräunlich, "
        "Christian Ribeaud, "
        "François Martin",
        author_email="Robin.Engler@sib.swiss, "
        "riccardo.murri@id.ethz.ch, "
        "jaroslaw.surkont@unibas.ch, "
        "gerhard.braeunlich@id.ethz.ch, "
        "christian.ribeaud@karakun.com, "
        "francois.martin@karakun.com",
        url="https://gitlab.com/biomedit/libbiomedit",
        install_requires=[
            "dataclasses ; python_version<'3.7'",
            "gpg-lite>=0.10.1",
        ],
        packages=find_packages(exclude=["test", "test.*"]),
        package_data={"libbiomedit": ["py.typed"]},
        zip_safe=False,
        python_requires=">=3.6",
        test_suite="test",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.6",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
            "Operating System :: OS Independent",
        ],
    )
