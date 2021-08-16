import setuptools
import versioneer

development_dependencies = ["black", "pytest", "versioneer", "coverage", "build"]

setuptools.setup(
    name="seedftw",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="PVF",
    author_email="pvf@dtime.ai",
    description="Simple Energy & Environment Data From The World (aka. seedftw) - A small example package for acquiring open energy and environment data",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Pierre_VF/seedftw",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy",
        "pandas",
        "plotly",
        "pytz",
        "requests",
        "setuptools",
        "xlrd",
    ],
    extras_require={
        "all": ["plotly"] + development_dependencies,
        "dev": development_dependencies,
    },
)

# More details on how to set this up: https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html
