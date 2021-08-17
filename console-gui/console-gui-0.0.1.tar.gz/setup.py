from setuptools import setup, find_packages

with open('README.md', 'r') as file:
    text = file.read()

setup(
    name='console-gui',
    version='0.0.1',    
    description='gui for conosle buttons and fields',
    long_description = text,
    long_description_content_type = 'text/markdown',
    
    
    url='https://github.com/shuds13/pyexample',
    author='levi dalrymple',
    license='file: LICENSE',
    packages=find_packages(),
    install_requires=[
        'colorama',
        'pynput'                
                      ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Operating System :: Microsoft :: Windows',        
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)