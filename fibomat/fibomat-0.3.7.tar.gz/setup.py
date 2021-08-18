import sys
import os
import pathlib
import shutil

from setuptools import find_packages, Extension

try:
    from skbuild import setup
    from skbuild.command.build_ext import build_ext
except ImportError:
    print('Please update pip, you need pip 10 or greater,\n'
          ' or you need to install the PEP 518 requirements in pyproject.toml yourself', file=sys.stderr)
    raise


class BokehExtension(Extension):
    def __init__(self, name, ext_dir):
        Extension.__init__(self, name, sources=[])
        self.ext_dir = os.path.abspath(ext_dir)


class BuildBokehExt(build_ext):
    def run(self):
        from bokeh.ext import build

        for ext in self.extensions:
            if not build(ext.ext_dir, rebuild=True):
                raise RuntimeError('Could not build bokeh extension.')

            out_path = os.path.abspath(os.path.dirname(self.get_ext_fullpath(ext.name)))
            shutil.copy2(
                f'{ext.ext_dir}/dist/bokeh-measuretool.min.js',
                f'{out_path}/fibomat/default_backends/bokeh-measuretool.min.js'
            )


here = pathlib.Path(__file__).parent.resolve()
long_description = (here / 'README.md').read_text(encoding='utf-8')


setup(
    name="fibomat",
    version="0.3.7",
    description="fib-o-mat is a toolbox to generate patterns for focused ion beam instruments.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Victor Deinhart',
    author_email='victor.deinhart@helmholtz-berlin.de',
    url='https://gitlab.com/viggge/fib-o-mat',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering :: Physics',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords='focused ion beam, fib, pattern, patterning, beam path generation,',
    license="GPLv3",
    packages=find_packages(exclude=['test*', 'custom_backends*']),
    python_requires='>=3.8',
    package_data={'fibomat': ['py.typed', 'default_backends/measure_band.ts']},
    cmake_install_dir='fibomat',
    ext_modules=[BokehExtension('bokeh-measuretool', 'bokeh-measuretool')],
    cmdclass={'build_ext': BuildBokehExt},
    install_requires=[
        'numpy', 'scipy', 'sympy', 'bokeh', 'pint', 'ezdxf', 'numba', 'vispy', 'pyqt5', 'splipy', 'frozenlist',
        'pillow', 'svgwrite', 'pyhershey', 'jinja2'
    ],
    extras_require={
        'docs': [
            'sphinx', 'recommonmark', 'pydata_sphinx_theme', 'sphinxemoji', 'bokeh'
        ],
        'testing': [
            'pytest', 'pytest-coverage', 'pytest-mock'
        ],
        'dev': [
            'bump2version', 'twine'
        ]
    },
    entry_points={
        'console_scripts': [
            'beam_simulation = fibomat.beam_simulation:run',
        ],
    },
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/viggge/fib-o-mat/-/issues',
        'Source': 'https://gitlab.com/viggge/fib-o-mat/',
        'Documentation': "https://fib-o-mat.readthedocs.io/en/latest/",
    },
)
