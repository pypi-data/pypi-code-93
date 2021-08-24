import pathlib
import setuptools

HERE = pathlib.Path(__file__).parent

README = (HERE / 'README.rst').read_text()

setuptools.setup(
    name='v-cloud-market-cli-user',
    version='0.0.1',
    description='V-Cloud Market-Cli User-End',
    long_description=README,
    long_description_content_type='text/x-rst',
    url='https://github.com/virtualeconomy/v-cloud-market-cli-user.git',
    author='hvoid-build-block',
    author_email='hvoid@v.systems',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3,6'
)