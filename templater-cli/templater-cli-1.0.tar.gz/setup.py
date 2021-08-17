from setuptools import setup, find_packages

setup(
    name='templater-cli',
    version='1.0',
    author='Sayam.py',
    author_email='sujata.howrah.belgachia@gmail.com',
    description='Template Managing Tool',
    url='https://github.com/sayampy/Template-Manager-Tool',
    long_description=open('README.md','r').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        
    ],
    license='MIT',
    classifiers =[

            "Programming Language :: Python :: 3", 

            "License :: OSI Approved :: MIT License", 

            "Operating System :: OS Independent", 

        ], 
    entry_points='''
        [console_scripts]
        tmt=templater.main:main
    ''',
)