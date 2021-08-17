from setuptools import setup


def version():
    with open('VERSION') as f:
        return f.read().strip()


def readme():
    with open('README.md') as f:
        return f.read()


def requirements():
    with open('requirements.txt') as f:
        return f.read().split('\n')


setup(
    name='teska_monitor',
    author='Said El Hadouchi',
    description="Monitoring Software",
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='GPL 3.0',
    version=version(),
    install_requires=requirements(),
    include_package_data=True,
)
