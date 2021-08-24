from setuptools import setup, find_packages

install_requires = [
    'numpy',
    'matplotlib'
]


setup(
    name="numerical_analysis",
    version="0.1.1",
    packages=find_packages(),

    author="IAGerogiannis",
    author_email='iagerogiannis@gmail.com',
    description="Numerical Analysis contains some basic numerical methods for solving equations, integrating "
                "functions and parameterizing curves with Bezier Polynomials.",
    url="https://github.com/iagerogiannis/numerical-analysis",
    install_requires=install_requires,
    license="BSD"
)
