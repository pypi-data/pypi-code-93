import setuptools
import versioneer

development_dependencies = ["black", "pytest", "versioneer", "coverage", "build"]

setuptools.setup(
    name="plotneat",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="PVF",
    author_email="pierrevf@live.fr",
    description="A simple library to make cleaner plots.",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Pierre_VF/plotneat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "IPython",
        "kaleido",
        "matplotlib",
        "numpy",
        "pandas",
        "plotly",
        "setuptools",
    ],
    extras_require={
        "all": development_dependencies,
        "dev": development_dependencies,
    },
)

# More details on how to set this up: https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html
