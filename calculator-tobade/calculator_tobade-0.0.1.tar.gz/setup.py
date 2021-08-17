import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read() 

setuptools.setup(
    name="calculator_tobade",
    version="0.0.1",
    author="Oluwatobi Adeniji",
    author_email="oluwatobiadeniji06@gmail.com",
    description="A basic calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TobAde/Calculator",
    project_urls={
        "Bug Tracker": "https://github.com/TobAde/Calculator.git/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    py_modules=["calculator"],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6"
)