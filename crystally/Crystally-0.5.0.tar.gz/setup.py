import setuptools

project_urls = {
         "Documentation": "https://crystally.readthedocs.io/",
     }

setuptools.setup(name='Crystally',
                 version='0.5.0',
                 description='Python module to model and analyze crystal structures',
                 url='https://git.rwth-aachen.de/john.arnold/Crystally.git',
                 author='John Arnold',
                 author_email='arnold@pc.rwth-aachen.de',
                 license='None',
                 packages=setuptools.find_packages(),
                 package_dir={'crystally': 'crystally'},
                 install_requires=['numpy', 'scipy>=1.7.0'],
                 python_requires='>=3.7',
                 project_urls=project_urls)
