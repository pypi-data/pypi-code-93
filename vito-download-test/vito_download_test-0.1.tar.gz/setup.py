from setuptools import setup, find_packages
import versioneer

setup(
    name='vito_download_test',
    version=0.1,
    # cmdclass=versioneer.get_cmdclass(),
    description='Download from land.copernicus.vgt.vito.be/PDF/datapool',
    author='Jonas Solvsteen',
    author_email='josl@dhigroup.com',
    url='https://www.dhigroup.com',
    packages=find_packages(),
    install_requires=[
            'itsybitsy_test'
        ],
    )
