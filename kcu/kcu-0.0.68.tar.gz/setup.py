import setuptools, os

readme_path = os.path.join(os.getcwd(), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r") as f:
        long_description = f.read()
else:
    long_description = 'kcu'

setuptools.setup(
    name="kcu",
    version="0.0.68",
    author="Kristof",
    description="some python utility methods that I often use compiled in a package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kkristof200/py_common_utils",
    packages=setuptools.find_packages(),
    install_requires=[
        'fake-useragent>=0.1.11',
        'requests>=2.26.0',
        'simple-multiprocessing>=0.0.15'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)