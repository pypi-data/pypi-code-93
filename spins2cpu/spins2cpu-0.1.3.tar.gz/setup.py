from setuptools import setup, find_packages

setup(
    name='spins2cpu',
    version='0.1.3',
    author='kan',
    author_email='luokan@hrbeu.edu.cn',
    python_requires=">=3.6",
    license='MIT',
    license_files=('LICENSE.txt',),
    platforms=['Unix', 'Windows'],
    keywords='Monte Carlo Simulation Ising Model',
    description='spins2cpu: A Monte Carlo Simulation Code for the Phase Transition in 2D/3D Materials',
    long_description=open('README.txt').read(),
    url='https://github.com/lkccrr/spins2cpu',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    install_requires=[
        'numba',
        'numpy',
        'matplotlib'
    ],
    entry_points={
        'console_scripts': ['spins2cpu=spins2cpu.wrapper:main']
    },
    packages=find_packages(),
    include_package_data=True
)