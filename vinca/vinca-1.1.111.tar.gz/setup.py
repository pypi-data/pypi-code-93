import setuptools



setuptools.setup(
    name="vinca",
    version="1.1.111",
    author="Oscar Laird", 
    data_files = [('man/man1', ['vinca.1'])],
    include_package_data = True,
    packages=setuptools.find_packages(),
    scripts = ['scripts/vinca','scripts/vinca_debug'] # TODO entry points the proper way
)
