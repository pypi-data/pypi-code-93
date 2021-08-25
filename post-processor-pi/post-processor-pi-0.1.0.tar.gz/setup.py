import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='post-processor-pi',
    version='0.1.0',
    license='MIT',
    author='Paolo Italiani',
    author_email='paoita@hotmail.it',
    description='Post processor for Document AI',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/paoloitaliani/post-processor-pi',
    packages=['dai_post_processor'],
    install_requires=[
        "numpy",
        "matplotlib"
    ],
)