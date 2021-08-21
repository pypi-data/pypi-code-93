import setuptools

with open("README", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="d4-py",
    version="0.0.0.10a2",
    author="ast.08",
    author_email="<ast.08e@gmail.com>",
    description="d4.py pre-alpha v0.0.0.10a",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/namuKR/d4.py",
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
    ],
    python_requires='>=3.6',
    install_requires=['requests', 'asyncio', 'aiohttp']
)
