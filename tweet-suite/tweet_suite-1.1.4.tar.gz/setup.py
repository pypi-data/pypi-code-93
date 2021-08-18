from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tweet_suite",
    version="1.1.4",
    author="Nina Di Cara, Alastair Tanner, Valerio Maggio",
    author_email="ninadicara@protonmail.com",
    description="Collect and save daily Twitter data from Wales using Twitter's Academic API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ninadicara/tweet-suite",
    include_package_data=True,
    project_urls={"Bug Tracker": "https://github.com/ninadicara/tweet-suite/issues",},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    scripts=["scripts/collect_tweets"],
    packages=find_packages(exclude=[]),
    python_requires=">=3.6,<3.10",
    install_requires=[
        "retry",
        "geopandas",
        "vaderSentiment",
        "schedule",
        "pandas",
        "shapley",
        "requests",
    ],
)
