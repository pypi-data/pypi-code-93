from setuptools import find_packages, setup


# Required dependencies
required = [
    "gym","pytest","matplotlib","pyvirtualdisplay"
]


setup(
    name='rl_helper',
    version="0.1.1",
    author="cywgoog@gmail.com",
    packages=find_packages("rl_helper"),
    include_package_data=True,
    install_requires=required
)