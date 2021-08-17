import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

# Version notes:
# 0.5.0-0.6.0 -> GijonIN OLD
# 0.6.1 -> GijonIN
# 0.7.0 -> CalidadAire
# 0.7.{1,2} -> CalidadAire cambios
# 0.8.0 -> 6LowPan
# 0.8.6 -> Valores 87, 88, 89 de Sock
# 0.8.9 -> Updated proxy dependencies
# 0.8.10 -> Updated naming when id is repeated
# 0.8.14 -> No poll when no devices
# 0.8.15 -> Catch timeout exception
# 0.8.16 -> Catch timeout exception during login
# 0.8.18 -> Sif bat baja
# 0.8.19 -> Añadido state
# 0.8.20 -> Arreglada intensidad y potencia reactiva cuando consumo es 0
# 0.8.21 -> Meterbus factor
# 0.8.22 -> Socks detect file
# 0.8.23 -> Added noise sensor

setuptools.setup(
    name="ingeniumpy",
    version="0.8.23",
    author="Daniel Garcia",
    author_email="dgarcia@ingeniumsl.com",
    description="Ingenium API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/ingeniumpy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "aiohttp>=3.6,<4.0",
    ],
    package_data={"ingeniumpy": ["bin/proxy*"]},
)
