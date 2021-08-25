from setuptools import setup


# WARNING! You must also specify all deps in requirements.txt!
setup(setup_requires=['pbr>=4.0,<5.6.0', 'wheel>=0.24', 'glob2>=0.4.1', 'packaging>=16.8'], pbr=True, long_description_content_type="text/markdown")

