from setuptools import setup, find_packages

setup(
    name="lastipy",
    # fmt: off
    version='1.1.36',
    # fmt: on
    description="Lastipy is a Python library combining the APIs of Spotify and Last.fm, with scripts for creating customized recommendation playlists, automatically saving new releases, etc.",
    url="http://github.com/evanjamesjackson/lastipy",
    author="Evan Jackson",
    author_email="evan@jacksonnet.ca",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "recommendations_playlist = scripts.recommendations_playlist:build_recommendations_playlist",
            "save_new_releases = scripts.save_new_releases:save_new_releases",
            "organize_favorites = scripts.organize_favorites:organize_favorites",
        ]
    },
    install_requires=[
        "numpy",
        "requests",
        "spotipy",
        "iso8601",
        "python-dateutil",
        "pytest",
        "wheel",
        "black"
    ]
)
