from setuptools import find_packages, setup

readme = ""

requirements = [
    "dask",
    "distributed",
    "owl-pipeline-develop",
]

setup_requirements = ["pytest-runner", "flake8"]

test_requirements = ["coverage", "pytest", "pytest-cov", "pytest-mock"]


setup(
    author="Eduardo Gonzalez Solares",
    author_email="e.gonzalezsolares@gmail.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Owl Shell Pipeline",
    entry_points={"owl.pipelines": "shell = shell_pipeline"},
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme,
    include_package_data=True,
    keywords="imaxt, owl",
    name="owl-shell-pipeline",
    packages=find_packages(include=["shell_pipeline*"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://eddienko.github.com/owl-shell-pipeline",
    version="0.2.0",
    zip_safe=False,
    python_requires=">=3.7",
)
