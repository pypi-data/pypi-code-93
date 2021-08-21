import setuptools

import versioneer

development_dependencies = [
    "black",
    "pytest",
    "versioneer",
    "coverage",
    "build",
    "pre-commit",
]

setuptools.setup(
    name="senasopt",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="PVF",
    author_email="pvf@dtime.ai",
    description="Simple Energy Asset Optimisation (aka. senasopt) - A small example package trying out optimisation of energy-related assets",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Pierre_VF/senasopt",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "casadi",
        "numpy",
        "pandas",
        "setuptools",
        "xlrd",
    ],
    extras_require={
        "all": ["plotly", "dash", "plotly"] + development_dependencies,
        "dev": development_dependencies,
    },
)

# More details on how to set this up: https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html
