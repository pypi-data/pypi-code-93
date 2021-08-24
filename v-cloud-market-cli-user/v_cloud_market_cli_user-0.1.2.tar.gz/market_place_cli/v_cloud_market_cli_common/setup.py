import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.md').read_text()


setuptools.setup(
    name='v-cloud-market-cli-commonlib',
    version='0.0.1',
    description='V-Cloud Market Cli Common Lib',
    long_description=README,
    long_description_content_type='text/markdown',
    author='hvoid-build-block',
    author_email='hvoid@v.systems',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.6'
)