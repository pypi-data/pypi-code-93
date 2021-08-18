import setuptools

with open('readme.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='idlea',
    version='0.0.8',
    author='Lishixian(znsoooo)',
    author_email='lsx7@sina.com',
    description='IDLE-Advance',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/znsoooo/IDLE-Advance',
    project_urls={
        'Bug Tracker': 'https://github.com/znsoooo/IDLE-Advance/issues',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages=['idlealib'],
    python_requires='>=3.6',
)
