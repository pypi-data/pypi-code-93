import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sts-models-tj", # Replace with your own username
    version="0.0.45",
    author="tj",
    author_email="tjbindseil@gmail.com",
    description="models for sts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tbindseil/sts-mono-repo",
    package_dir={'': 'src'},  # Optional
    packages=setuptools.find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['sqlalchemy'],
    python_requires='>=3.6',
)
