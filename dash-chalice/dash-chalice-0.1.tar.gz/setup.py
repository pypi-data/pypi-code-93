from setuptools import setup

setup(
    name="dash-chalice",
    version="0.1",
    description="Chalice as an alternative to Flask for Plotly Dash",
    url="https://github.com/ellwise/dash-chalice",
    author="Elliott Wise",
    author_email="ell.wise@gmail.com",
    license="GNU GPL v3",
    packages=["dash_chalice"],
    install_requires=["dash", "chalice"],
    zip_safe=False,
)
