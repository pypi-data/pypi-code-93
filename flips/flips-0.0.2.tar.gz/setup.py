from setuptools import setup

setup(
    name='flips',
    version='0.0.2',
    description='Flips solver',
    url='https://gitlab.inria.fr/dlunz/flips',
    author='Davin Lunz',
    author_email='davin.lunz@inria.fr',
    license='cecill-2.1',
    packages=['flips'],
    install_requires=['tqdm','scipy','numpy'],
    zip_safe=False
)
