from setuptools import setup, find_packages

# See note below for more information about classifiers
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Education",
    "Operating System :: POSIX :: Linux",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: MacOS",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
]

setup(
    name="dismusic",
    version="1.0.1",
    description="A music cog for any discord.py bot",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/shahprog/dismusic/",
    author="Md Shahriyar Alam",
    author_email="mdshahriyaralam552@gmail.com",
    license="MIT",
    classifiers=classifiers,
    keywords="discord discord-music music-bot discord-music-bot lavalink wavelink",
    packages=find_packages(),
    install_requires=["discord.py", "wavelink"],
)
