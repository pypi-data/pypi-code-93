import setuptools


VERSION = '0.1'

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()


setuptools.setup(
    name="grip-mbmasuda",
    version=VERSION,
    author="Mari Masuda",
    author_email="mbmasuda.github@gmail.com",
    description="Generic rate-limited item processor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mbmasuda/generic-rate-limited-item-processor",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
