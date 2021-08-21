import setuptools

import versioneer

dash_dependencies = ["dash", "plotly"]
fastapi_dependencies = ["fastapi[all]"]
development_dependencies = [
    "black",
    "pytest",
    "versioneer",
    "coverage",
    "build",
    "pre-commit",
]

setuptools.setup(
    name="apihelpers4py",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="PVF",
    author_email="pvf@dtime.ai",
    description="Helpers for API development",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Pierre_VF/apihelpers4py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas",
        "requests",
        "dateutils",
    ],
    extras_require={
        "fastapi": fastapi_dependencies,
        "dash": dash_dependencies,
        "dev": development_dependencies + fastapi_dependencies,
    },
)

# More details on how to set this up: https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html
