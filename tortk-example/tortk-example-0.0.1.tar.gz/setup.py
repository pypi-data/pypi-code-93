import setuptools

with open("/workspace/TorToolkit-Telegram/readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tortk-example",
    version="0.0.1",
    author="reaitten",
    author_email="vconner806@gmail.com",
    description="A awesome Torrent Leecher!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yash-dk/TorToolkit-Telegram/tree/alpha",
    project_urls={
        "Bug Tracker": "https://github.com/yash-dk/TorToolkit-Telegram/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "tortoolkit"},
    packages=setuptools.find_packages(where="tortoolkit"),
    python_requires=">=3.6",
)