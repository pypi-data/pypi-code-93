from setuptools import find_packages
from numpy.distutils.core import setup, Extension


ext1 = Extension(name='interpolate_fields',
                 sources=['hn2016_falwa/interpolate_fields.f90'],
                 f2py_options=['--quiet'])

ext2 = Extension(name='compute_reference_states',
                 sources=['hn2016_falwa/compute_reference_states.f90'],
                 f2py_options=['--quiet'])

ext3 = Extension(name='compute_lwa_and_barotropic_fluxes',
                 sources=['hn2016_falwa/compute_lwa_and_barotropic_fluxes.f90'],
                 f2py_options=['--quiet'])


setup(
    name='hn2016_falwa',
    version='0.5.0',
    description='python package to compute finite-amplitude local wave activity (Huang and Nakamura 2016, JAS)',
    url='https://github.com/csyhuang/hn2016_falwa',
    author='Clare S. Y. Huang',
    author_email='csyhuang@uchicago.edu',
    license='MIT',
    packages=find_packages(),
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    ext_modules=[ext1, ext2, ext3],
    zip_safe=False
)
