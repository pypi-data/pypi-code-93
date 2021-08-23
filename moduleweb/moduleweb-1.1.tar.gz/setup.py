import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moduleweb",
    version="1.1",
    author = "MEB",
    author_email = "egorikhelp@gmail.com",
    keywords = "moduleweb web python library aiohttp jinja2 framework",
    description = "A simple, clear and friendly library written in Python for faster and more convenient application development on the Aiohttp framework🎍",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/machnevegor/ModuleWeb",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    packages=["moduleweb"],
    install_requires=["aiohttp", "jinja2", "aiohttp_jinja2"],
    python_requires=">=3.7"
)
