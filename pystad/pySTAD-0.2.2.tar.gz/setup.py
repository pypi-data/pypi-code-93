from __future__ import print_function
# --- Required imports
import os
import sys
import glob
import numpy as np
import os.path as op
from distutils import log
from collections import defaultdict
from jupyter_packaging import npm_builder
from setuptools import setup, find_packages, Extension
# --- Commands to customize
from wheel.bdist_wheel import bdist_wheel
from setuptools.command.sdist import sdist 
from setuptools.command.develop import develop
from setuptools.command.install import install
from distutils.command.install_data import install_data
# --- Errors to catch to detect if Cython extensions compiled properly.
from distutils.errors import CCompilerError, DistutilsExecError, DistutilsPlatformError


# --- Configure logging
log.set_verbosity(log.DEBUG)
log.info('setup.py entered')


# --- Configure Jupyter Lab extension
# The jupyter lab widget has a JavaScript front-end that needs to be build
# and installed . The sdist, bdist_wheel, and develop commands are wrapped
# to make sure the widget is build in source and binary bundles. The
# install_data command is wrapped to install the widget to where jupyter-lab
# expects it to be, respecting conda environments etc...
here = op.dirname(op.abspath(__file__))
js_dir = op.join(here, 'js')
js_source_dir = op.join(js_dir, 'src')
js_build_dir = op.join(js_dir, 'lib')
builder = npm_builder(js_dir, build_dir=js_build_dir, 
                      source_dir=js_source_dir, npm='npm')


# --- Configure Cython extensions
# There are three possibilities:
# 1. Cythonize and compile the extensions (from .pyx to .c to platform 
#    specific library). This option is used when the Cython package is
#    available as setup requirement (i.e. it can be imported in this file).
#    This option is used in development environments. The sdist and 
#    bdist_wheel commands are wrapped to cythonize the extensions when run
#    making sure the .c files are always up to date in source and binary
#    bundles of the package.
# 2. Only compile the pre-bundled .c files as extensions. This option
#    is used when installing the package without Cython installed.
#    bdist_wheel and sdist are not wrapped for Cython in this case.
# 3. Use python fallback implementation when options 1 and 2 fail.

# Case 1 and 2:
#   Check if Cython is available during setup
try:
  from Cython.Build import cythonize
  from Cython.Distutils import build_ext
  log.info('Using Cython source for extensions.')
  cythonize_extensions = True
  cython_ext = '.pyx'
except ImportError as ex:
  from setuptools.command.build_ext import build_ext
  log.info(ex)
  log.info('Using distributed Cython modules (.c) for extensions.')
  cythonize_extensions = False
  cython_ext = '.c'


# --- Create Cython extensions
# The .pyx files are present in source distributions of this package, so 
# we can use them to detect extensions even if we will use pre-generated
# .c files.
def create_extensions():
  extension_files = [f for f in glob.glob('stad/**/*.pyx', recursive=True) if op.isfile(f)]
  extension_packages = [
      f.replace('.pyx', '').replace(op.sep, '.') 
      for f in extension_files
  ]
  extensions = [
    Extension(extension_packages[idx], [extension_files[idx].replace('.pyx', cython_ext)],
              define_macros = [("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
              include_dirs=[np.get_include()])
    for idx in range(len(extension_files))
  ]
  return extensions


extensions = create_extensions()
if cythonize_extensions:
  extensions = cythonize(extensions, language_level=3)


# --- Wrap commands
# Build Jupyter front-end and cythonize extensions
class develop_wrapped(develop):
  def run(self):
    builder()
    if cythonize_extensions:
      self.run_command('build_ext')
    develop.run(self)
    self.run_command('install_data')

# Build Jupyter front-end and cythonize extensions
class bdist_wheel_wrapper(bdist_wheel):
  def run(self):
    builder()
    if cythonize_extensions:
      self.run_command('build_ext')
    super().run()

# Build Jupyter front-end and cythonize extensions
class sdist_wrapper(sdist):
  def run(self):
    builder()
    if cythonize_extensions:
      self.run_command('build_ext')
    super().run()

# Expand wildcards when installing data.
class install_data_wrapper(install_data):
  def finalize_options(self):
    super().finalize_options()
    expanded_data_files = []

    for target in self.distribution.data_files:
      # Store sub-directory & files in them
      files = defaultdict(list)
      for p in target[1]:
        base = op.dirname(p)
        for f in glob.glob(p, recursive=True):
          if op.isfile(f):
            sub_path = op.dirname(op.relpath(f, base)).replace(op.sep, '/')
            files[sub_path].append(f.replace(op.sep, '/'))
      
      # Update data_files while maintaining subdirectory structure
      for base, paths in files.items():
        expanded_data_files.append((
          target[0] + '/' + base if base else target[0],
          paths
        ))

    # Set the expanded data_files lists so it is used during `run()`
    self.distribution.data_files = expanded_data_files
    self.data_files = expanded_data_files

# Add OpenMP commands for compiling extensions
class build_ext_wrapper(build_ext):
  def build_extensions(self):
    openmp_flag = self.get_openmp_flag()

    for e in self.extensions:
      e.extra_compile_args += openmp_flag
      e.extra_link_args += openmp_flag

    super().build_extensions()

  def get_openmp_flag(self):
    if hasattr(self.compiler, 'compiler'):
      compiler = self.compiler.compiler[0]
    else:
      compiler = self.compiler.__class__.__name__

    if sys.platform == "win32" and ('icc' in compiler or 'icl' in compiler):
      return ['/Qopenmp']
    elif sys.platform == "win32":
      return ['/openmp']
    elif sys.platform in ("darwin", "linux") and "icc" in compiler:
      return ['-qopenmp']
    elif sys.platform == "darwin" and 'openmp' in os.getenv('CPPFLAGS', ''):
      # -fopenmp can't be passed as compile flag when using Apple-clang.
      # OpenMP support has to be enabled during preprocessing.
      return []
    # Default flag for GCC and clang:
    return ['-fopenmp']


# --- Run Setup
cmdclass = {
  'sdist': sdist_wrapper,
  'develop': develop_wrapped,
  'build_ext': build_ext_wrapper,
  'bdist_wheel': bdist_wheel_wrapper,
  'install_data': install_data_wrapper,
}

# Try to build the package with Cython extensions
ext_errors = (CCompilerError, DistutilsExecError, DistutilsPlatformError, IOError, SystemExit)
try:
  setup(cmdclass = cmdclass, ext_modules = extensions)
  failed_building_extensions = False
except ext_errors as ex:
  log.warn(ex)
  log.warn('The Cython extensions could not be build, falling back on '
            'the python implementations')
  failed_building_extensions = True


if failed_building_extensions:
  del cmdclass['build_ext']
  setup(cmdclass = cmdclass)
  log.warn('Installed pySTAD without Cython extensions')
