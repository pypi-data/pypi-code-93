from pathlib import Path
from setuptools import find_packages, setup

with Path('requirements.txt').open() as fin:
    install_requires = [r.strip() for r in fin.readlines()
                        if r.strip() and not r.strip().startswith('#')]
# install_requires = 'wheel click coverage GitPython pytest-cov Sphinx flake8 python-dotenv pathlib2 wheel'.split()

# backwards compatibility


setup(
    url='https://gitlab.com/prosocialai/proai',
    author_email='hobson@proai.org',
    name='proai',
    packages=find_packages(),
    install_requires=install_requires,
    version='0.0.4',
    description='Tools and AI for building prosocial AI algorithms.',
    author='Hobson Lane (ProAI.org)',
    license='Hippocratic License (MIT + Do No Harm)',
)
