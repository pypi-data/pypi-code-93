from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ElectronBonder",
    url="https://github.com/RockefellerArchiveCenter/ElectronBonder",
    description="Project Electron Client Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rockefeller Archive Center",
    author_email="archive@rockarch.org",
    version="0.8",
    license='MIT',
    packages=find_packages(),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires=">=2.7",
    install_requires=[
        "requests",
        "six",
    ],
)
