from setuptools import setup, find_packages

with open('README.md', encoding="utf-8") as readme_file:
    README = readme_file.read()

with open('HISTORY.md', encoding="utf-8") as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='epkeeperlib',
    version='1.0.8',
    author='Cheng Chen',
    author_email='tonychengchen@hotmail.com',
    description='EPKEEPER common utility package',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    url='https://gitee.com/tonychengchen/epkeeper_lib',
)

with open("requirements.txt", "r") as f:
    install_requires = f.read().split("\n")

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
