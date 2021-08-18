import os
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

requirements_txt = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "requirements.txt"
)
install_requires = []  # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirements_txt):
    with open(requirements_txt) as f:
        install_requires = f.read().splitlines()

setup(
    name="cppcheck_codequality",
    license="MIT",
    author="Alex Hogen",
    author_email="code.ahogen@outlook.com",
    description="Convert a CppCheck XML report to a GitLab-compatible Code Quality JSON report",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/ahogen/cppcheck-codequality",
    project_urls={
        "Source": "https://gitlab.com/ahogen/cppcheck-codequality",
        "Tracker": "https://gitlab.com/ahogen/cppcheck-codequality/-/issues"
    },
    setup_requires=["setuptools_scm"],
    use_scm_version={
        "local_scheme": "no-local-version",
        "write_to": "src/version.py",
        "write_to_template": "# pylint: disable=C0114\nVERSION = '{version}'",
    },
    install_requires=install_requires,
    # https://docs.python.org/3/distutils/examples.html#pure-python-distribution-by-module
    package_dir={"cppcheck_codequality": "src"},
    packages=["cppcheck_codequality"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    # https://setuptools.readthedocs.io/en/latest/setuptools.html#automatic-script-creation
    entry_points={
        "console_scripts": ["cppcheck-codequality=cppcheck_codequality:main"],
    },
    python_requires=">=3.6",
)
