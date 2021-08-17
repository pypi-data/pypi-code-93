from setuptools import find_packages
from setuptools import setup

setup(
    name="gitlab-auto-mr",
    version="1.1.5",
    description="A simple tool for automatically creating merge requests in GitLab",
    long_description=open("README.rst").read(),
    long_description_content_type="text/x-rst",
    author="Haseeb Majid",
    author_email="me@haseebmajid.com",
    keywords="Python",
    license="Apache License",
    url="https://gitlab.com/gitlab-automation-toolkit/gitlab-auto-mr",
    python_requires="~=3.6",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    zip_safe=False,
    include_package_data=True,
    install_requires=["click>=7.0", "python-gitlab>=2.0.0"],
    entry_points={"console_scripts": ["gitlab_auto_mr = gitlab_auto_mr.cli:cli"]},
    classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
