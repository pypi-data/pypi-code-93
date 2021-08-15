import os
import pathlib
from distutils.command.install_data import install_data

from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext


class CMakeExtension(Extension):

    def __init__(self, name):
        # don't invoke the original build_ext for this special extension
        super().__init__(name, sources=[])


class BuildExt(build_ext):
    """
    自定义了 build_ext 类，对 CMakeExtension 的实例，调用 CMake 和 Make 命令来编译它们
    """

    def run(self):
        for ext in self.extensions:
            if isinstance(ext, CMakeExtension):
                self.build_cmake(ext)
        # super().run()

    def build_cmake(self, ext):
        cwd = pathlib.Path().absolute()

        build_temp = f"{pathlib.Path(self.build_temp)}/{ext.name}"
        os.makedirs(build_temp, exist_ok=True)

        extdir = pathlib.Path(self.get_ext_fullpath(ext.name))
        # extdir.mkdir(parents=True, exist_ok=True)

        config = "Debug" if self.debug else "Release"
        cmake_args = [
            "-DCMAKE_LIBRARY_OUTPUT_DIRECTORY=" +
            os.path.join(str(extdir.parent.absolute()),
                         f'../{ext.name}/build'),
            "-DCMAKE_BUILD_TYPE=" + config
        ]

        build_args = [
            "--config", config,
            "--", "-j4"
        ]

        os.chdir(build_temp)
        self.spawn(["cmake", f"{str(cwd)}/{ext.name}"] + cmake_args)
        if not self.dry_run:
            self.spawn(["cmake", "--build", "."] + build_args)
        os.chdir(str(cwd))


class InstallCMakeLibsData(install_data):
    """
    Just a wrapper to get the install data into the egg-info

    Listing the installed files in the egg-info guarantees that
    all of the package files will be uninstalled when the user
    uninstalls your package through pip
    """

    def run(self):
        """
        Outfiles are the libraries that were built using cmake
        """

        # There seems to be no other way to do this; I tried listing the
        # libraries during the execution of the InstallCMakeLibs.run() but
        # setuptools never tracked them, seems like setuptools wants to
        # track the libraries through package data more than anything...
        # help would be appriciated

        self.outfiles = self.distribution.data_files


setup(
    name='algorithm-tool',
    version='0.2',
    packages=['algorithm_tool_nlp', 'algorithm_tool_nlp.algorithm_tool_core'],
    ext_modules=[CMakeExtension('algorithm_tool_nlp/algorithm_tool_core')],
    cmdclass={
        'build_ext': BuildExt,
        'install_data': InstallCMakeLibsData,
    },
    exclude_package_data={"": ["*.cxx"]}
)
