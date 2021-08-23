from setuptools import setup, find_packages

setup_args = dict(
    name='epkeeperlib',
    version='1.0.7',
    author='Cheng Chen',
    author_email='tonychengchen@hotmail.com',
    description='EPKEEPER common utility package',
    long_description="",
    license='MIT',
    packages=find_packages(),
    url='https://gitee.com/tonychengchen/epkeeper_lib',
)

with open("requirements.txt", "r") as f:
    install_requires = f.read().split("\n")

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
