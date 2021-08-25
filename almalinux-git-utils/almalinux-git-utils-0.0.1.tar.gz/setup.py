from setuptools import find_namespace_packages, setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name="almalinux-git-utils",
    version="0.0.1",
    author="Eugene Zamriy",
    author_email="ezamriy@almalinux.org",
    description="Utilities for working with the AlmaLinux OS Git server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://git.almalinux.org/almalinux/almalinux-git-utils",
    project_urls={
        "Bug Tracker": "https://git.almalinux.org/almalinux/almalinux-git-utils/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    packages=find_namespace_packages(include=['almalinux.*']),
    entry_points={
        'console_scripts': [
            'alma_blob_upload=almalinux.gitutils.blob_upload:main',
            'alma_get_sources=almalinux.gitutils.get_sources:main'
        ]
    },
    install_requires=[
        'boto3>=1.15.15',
        'requests>=2.20.0'
    ],
    python_requires=">=3.6",
    zip_safe=False
)
