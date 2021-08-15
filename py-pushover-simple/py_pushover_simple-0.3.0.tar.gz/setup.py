import setuptools

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name="py_pushover_simple",
    version="0.3.0",
    author="Matthew Jorgensen",
    author_email="matthew@jrgnsn.net",
    description="A wrapper for sending push notifications with Pushover",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://git.sr.ht/~mjorgensen/py_pushover_simple",
    project_urls={
        "Code": "https://git.sr.ht/~mjorgensen/py_pushover_simple",
        "Issue Tracker": "https://todo.sr.ht/~mjorgensen/py_pushover_simple",
    },
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Environment :: Plugins",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Natural Language :: English",
        "Topic :: Communications",
        "Topic :: Utilities",
    ),
)
