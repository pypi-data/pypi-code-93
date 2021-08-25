from setuptools import setup, find_packages

setup(
    name='pokemonPalette',
    version='0.0.1',
    description='The pokemonPalette is a python library generate a color palette based on the colors of a chosen pokemon.',
    author='Rodrigo M Calegari',
    author_email='rodrigomcalegari@gmail.com',
    license='MIT',
    packages= find_packages('pokemon_palette','pokemon_palette.*','pokemonPalette'),
    install_requires = [
        'opencv-python',
        'numpy',
        'matplotlib',
        'pokebase',
        'sklearn'
    ],
    url='https://github.com/MilanCalegari/pokemonPalette'
)