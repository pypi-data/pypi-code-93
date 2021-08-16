from setuptools import setup

with open("README.md", "r") as fh:
    readme = fh.read()

setup(
    name='asses-loopt-be',
    version='0.0.2',
    url='https://github.com/Loopt-GitHub-Organization/asses-loopt-be',
    license='MIT License',
    author='João Vitor Biston Nunes',
    long_description=readme,
    long_description_content_type="text/markdown",
    author_email='joaobiston@loopt.com.br',
    keywords='asses loopt be analysis utils machine learning booking evolution',
    description=u'Métdos uteis usados pela equipe de machine leaning da loopt',
    packages=['AssesLooptBE'],
    install_requires=[],
)