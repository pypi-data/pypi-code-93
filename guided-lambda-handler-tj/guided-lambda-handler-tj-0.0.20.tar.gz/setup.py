import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="guided-lambda-handler-tj", # Replace with your own username
    version="0.0.20",
    author="tj",
    author_email="tjbindseil@gmail.com",
    description="lambda handling framework",
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
    install_requires=['sts-validate-authentication-aws-cognito-tj', 'sts-json-datetime >= 0.0.8', 'sts-db-utils-tj'],
    python_requires='>=3.6',
)
