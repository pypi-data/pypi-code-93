import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="auto-retry-sshfs",
    version="1.0.0",
    author="Kavi Gupta",
    author_email="autoretrysshfs@kavigupta.org",
    description="Ridiculous tool that automatically retries sshfs for you over an unreliable connection.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kavigupta/auto-retry-sshfs",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    entry_points={
        "console_scripts": ["auto-retry-sshfs=auto_retry_sshfs.cli:cli"],
    },
)
