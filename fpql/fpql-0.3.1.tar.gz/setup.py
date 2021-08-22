import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fpql", # Replace with your own username
    version="0.3.1",
    author="ROSLI MOHD SANI",
    author_email="romsey67@gmail.com",
    description="A python package for financial instruments using QuantLib",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/romsey67/fpql-project.git",
    packages=setuptools.find_packages(),
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = ["QuantLib",
                        "pydantic",
                        "typing-extensions",
                        'numpy',
                        
    ],
    python_requires='>=3.6',
)
