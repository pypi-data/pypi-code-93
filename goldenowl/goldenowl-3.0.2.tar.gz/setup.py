from setuptools import setup
setup(
    name = 'goldenowl',         # Name of pip install package 
    packages = [
                'goldenowl',
                'goldenowl.asset',
                'goldenowl.portfolio'
                ],   # All packages in the project
    version = '3.0.2',      # Canonical versioning
    license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
    author = 'Nishanth (nishanth-)',
    author_email = '',
    url = 'https://github.com/nishanth-/goldenowl',   # Link to home page
    download_url = 'https://github.com/nishanth-/goldenowl/archive/refs/tags/v_302.tar.gz',    # Link to release tar file
    keywords = ['finance', 'investment', 'quant'],
    install_requires=[            # All dependencies from pipreqs <folder>
                      'pandas>=1.1.5',
                      'xirr>=0.1.6',
                     ],
    classifiers=[
        'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',      # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   # License
        'Programming Language :: Python :: 3',      #Supported versions
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
