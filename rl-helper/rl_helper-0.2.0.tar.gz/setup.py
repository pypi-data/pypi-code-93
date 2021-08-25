from setuptools import find_packages, setup


# Required dependencies
required = [
    "gym","pytest","matplotlib","pyvirtualdisplay"
]


setup(
    name='rl_helper',
    version="0.2.0",
    author="cywgoog@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=required
)