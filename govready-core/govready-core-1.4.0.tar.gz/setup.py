from setuptools import find_packages
from setuptools import setup

with open("version", 'r') as f:
    version = f.read().strip()

setup(
    name="govready-core",
    version=version,
    packages=find_packages(),
    author="Alexander Ward",
    author_email="alexander.ward1@gmail.com",
    url="https://github.com/GovReady/govready-core",
    description="This is the Core module for GovReady products",
    license="GNU",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.6",
    zip_safe=False,
    include_package_data=True,
    entry_points={
        'console_scripts': ['readycheck=govready_core.bin.healthcheck:run'],
    },
    install_requires=['requests', 'pyyaml'],
    extras_require={}
)
