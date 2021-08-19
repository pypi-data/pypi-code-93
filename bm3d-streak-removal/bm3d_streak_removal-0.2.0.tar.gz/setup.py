from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="bm3d_streak_removal",
    version='0.2.0',
    description='Ring artifact attenuation through multiscale collaborative filtering of correlated noise in sinogram domain',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    author='Ymir Mäkinen',
    author_email='ymir.makinen@tuni.fi',
    packages=['bm3d_streak_removal'],
    python_requires='>=3.5',
    install_requires=['numpy', 'scipy', 'bm3d'],
    ext_modules=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: Free for non-commercial use',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
