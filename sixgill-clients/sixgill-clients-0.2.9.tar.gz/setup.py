import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

with open('requirements.txt') as f:
    install_reqs = f.readlines()
    reqs = [str(ir) for ir in install_reqs]

with open('test_requirements.txt') as f:
    install_test_reqs = f.readlines()
    test_reqs = [str(ir) for ir in install_test_reqs]

setuptools.setup(
    name="sixgill-clients",
    version="0.2.9",
    author="Sixgill",
    author_email="getstarted@cybersixgill.com",
    description="Sixgill clients package",
    install_requires=reqs,
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/sixgill/sixgill-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    tests_require=test_reqs,
    test_suite="tests",
)
