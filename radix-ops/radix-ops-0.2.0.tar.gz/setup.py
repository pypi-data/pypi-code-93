import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='radix-ops',
    version='0.2.0',
    author='Debashish Palit',
    author_email='dpalit17@outlook.com',
    description='Convert between radices and perform arithmetic.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/deb17/radix',
    packages=['radix'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6'
)
