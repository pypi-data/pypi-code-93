import setuptools

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="IRonTeste",
    version="0.0.5",
    author="berre",
    packages=["Phi"],
    include_package_data=True,
    package_data={"phi": ['phi.dll'],"phi_linux":['phi_linux.so']},
    author_email="berreergunn@gmail.com",
    description="A sample test package",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/gituser/test-tackage",
    license='MIT',
    python_requires='>=2',
    install_requires=[]
)