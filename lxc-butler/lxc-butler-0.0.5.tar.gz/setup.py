import setuptools
import lxcb.info as info

setuptools.setup(
    name='lxc-butler',
    version=info.__version__,
    author=info.__author__,
    author_email=info.__author_email__,
    description=('A helper to make working with LXC containers easy and '
                 'convenient'),
    url=info.__url__,
    license=info.__license__,
    packages=['lxcb'],
    entry_points={
        'console_scripts': ['lxcb=lxcb.main:main']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Operating System :: POSIX :: Linux',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.6',
)
