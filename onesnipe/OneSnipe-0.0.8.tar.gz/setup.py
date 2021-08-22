import setuptools


setuptools.setup(
    name="OneSnipe",
    version="0.0.8",
    author="Geographs",
    author_email="87452561+Geographs@users.noreply.github.com",
    description="The successor of GeoSnipe, a pythonic Minecraft username sniper based on AsyncIO.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Geographs/OneSnipe",
    project_urls={
        "GitHub": "https://github.com/Geographs/OneSnipe",
        "Documentation": "https://docs.onesnipe.xyz/",
        "Bug Tracker": "https://github.com/Geographs/OneSnipe/issues",
        "Website": "https://onesnipe.xyz"
    },
    classifiers=[
        "Programming Language :: Python :: 3.9"
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.9",
    entry_points={"console_scripts": ["onesnipe=onesnipe.__main__:main"]},
    install_requires=[
        "aiohttp==3.7.4.post0",
        "msmcauth==0.0.3",
        "typer==0.3.2"
    ]
)
