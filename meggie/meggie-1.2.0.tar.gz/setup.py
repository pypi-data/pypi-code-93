from setuptools import setup

setup(
    name='meggie',
    version='1.2.0',
    description="User-friendly graphical user interface to do M/EEG analysis",
    author='CIBR',
    author_email='erkka.heinila@jyu.fi',
    url='https://github.com/cibr-jyu/meggie',
    license='BSD',
    packages=['meggie'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'mne>=0.23.0',
        'matplotlib',
        'scikit-learn',
        'python-json-logger',
        'pyqt5',
    ],
    entry_points={
        'console_scripts': ['meggie=meggie.run:main'],
    },
)
