from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyChiaLogProcessor',
    version='0.0.12',
    description='Chia plots log porcessor',
    py_modules=['pyChiaLogProcessor'],
    package_dir={'': 'src'},
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xh-dev-py/xh_py_chia_log_processor",
    author="xethhung",
    author_email="pypi@xethh.dev",
    extras_require={
        "dev": [
            "pytest>=3.7",
        ]
    }
)
