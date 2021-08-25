import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nutrimium",
    version="0.0.3",
    author="Yann Feunteun",
    author_email="yann.feunteun@protonmail.com",
    description="Command Line Interface for Nutrimium",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nutrimium/nutrimium-cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
          'typer',
          'requests'
      ],
    entry_points='''
    [console_scripts]
    nutrimium=nutrimium:app
    '''
)
