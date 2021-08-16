from setuptools import setup, find_packages
 
setup(
    name='responsivetone',
    version='1.4',
    description='Convert dialects and sentences using artificial intelligence.',
    long_description='-',
    author='Osawa Yuto',
    author_email='osawa_yuto@yahoo.co.jp',
    url='https://osawayuto.ngrok.io/',
    license='-',
    packages=find_packages()

)


install_requires=[
    "argparse"
    "requests"
    "json"
    "time"
]