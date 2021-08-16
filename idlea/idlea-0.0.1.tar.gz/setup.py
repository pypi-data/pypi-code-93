import setuptools

with open('readme.md', 'r') as f:
    long_description = f.read()

setuptools.setup(
    name='idlea',
    version='0.0.1',
    author='Lishixian(znsoooo)',
    author_email='lsx7@sina.com',
    description='IDLE-Advance',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/znsoooo/IDLE-Advance',
    packages=['idlealib'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='==3.6',
)
