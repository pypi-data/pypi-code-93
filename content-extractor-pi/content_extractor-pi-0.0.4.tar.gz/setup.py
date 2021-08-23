import setuptools

REQUIREMENTS = [i.strip() for i in open("requirements.txt").readlines()]
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='content_extractor-pi',
    version='0.0.4',
    license="MIT",
    author='Paolo Italiani',
    author_email='paoita@hotmail.it',
    description='Content extractor for files containing text',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/qarik/data-science/gcp_docunderstanding_spike/-/tree/content_extractor',
    packages=['content_extractor'],
    install_requires=REQUIREMENTS,
)
