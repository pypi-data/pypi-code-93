import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='normandy',
    version='0.2.3',
    author='Eloy Chang',
    author_email="echang.epsilondl@gmail.com",
    description='A data pipeline framework.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/echang1802/normandy",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'normandy = normandy.normandy:run'
        ]
    }
)
