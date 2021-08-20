from setuptools import setup

setup(
	name = "python-acrcloud",
	version = "1.2",
	description = "Detects the songs from an audio",
	long_description = "README.md",
	long_description_content_type = "text/markdown",
	license = "CC BY-NC-SA 4.0",
    python_requires = ">=3.7",
	author = "An0nimia",
	author_email = "An0nimia@protonmail.com",
	url = "https://github.com/An0nimia/acrcloud",
	packages = ["acrcloud"],
	install_requires = ["requests"]
)