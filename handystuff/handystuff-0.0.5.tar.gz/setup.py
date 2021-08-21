import sys

from setuptools import setup, find_packages

# Load requirements.txt
with open("requirements.txt") as requirements_file:
    lines = requirements_file.read().splitlines()
    install_requirements = []
    for line in lines:
        if '#egg' in line:
            name = line.split("#egg=")[-1]
            install_requirements.append(f"{name} @ {line}")
        else:
            install_requirements.append(line)

# make pytest-runner a conditional requirement,
# per: https://github.com/pytest-dev/pytest-runner#considerations
needs_pytest = {"pytest", "test", "ptr"}.intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setup_requirements = [
                         # add other setup requirements as necessary
                     ] + pytest_runner

setup(
    name='handystuff',
    version='0.0.5',
    description='Handy stuff that I end up copy-pasting from here and there',
    url='http://github.com/schlevik/handystuff',
    long_description=open("README.MD").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3.6",
        ],
    author='Viktor Schlegel',
    author_email='vtschlegel@gmail.com',
    license='GPLv3',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=install_requirements,
    setup_requires=setup_requirements,
    tests_require=["pytest"],
    include_package_data=True,
    python_requires=">=3.7",
    package_data={"handystuff": ["resources/*"]},
    zip_safe=False,
    extras_require={
        'stats': ['statsmodels>=0.12', 'scipy>=1.6.0', 'numpy>=1.18'],
    }
)
