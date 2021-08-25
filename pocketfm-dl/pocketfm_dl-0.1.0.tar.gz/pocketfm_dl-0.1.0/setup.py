from setuptools import setup

VERSION = "0.1.0"
DESCRIPTION="Downloader for PocketFM"
LONG_DESC=open("./README.md", "r").read()

setup(
        name="pocketfm_dl",
        version=VERSION,
        description=DESCRIPTION,
        scripts=["pocketfm-dl"],
        install_requires=[
            "jinja2",
            "requests"
            ]
        )
