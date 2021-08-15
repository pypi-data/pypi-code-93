from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='steamnews',
    version='0.1',
    description='Wrapper for the SteamNews Webapi',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Mert Demirbilek',
    author_email='MertDemirbilek@outlook.de',
    keywords=['steam', 'steamnews', 'Steam News'],
    url='https://github.com/Kamigiri/steamnews',
    download_url='https://pypi.org/project/steamnews/'
)

install_requires = [
    'requests'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)