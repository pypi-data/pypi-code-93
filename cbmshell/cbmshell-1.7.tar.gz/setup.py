from setuptools import setup

setup(name='cbmshell',
      description='Interactive shell to manipulate Commodore files',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      packages=['cbm_shell', 'cbm_shell/scripts'],
      entry_points={
        'console_scripts': [
          'cbm-shell = cbm_shell.scripts.cbm_shell:main'
          ]
        },
      install_requires = ['cbmcodecs2', 'cbmfiles', 'cmd2', 'd64', 't64', 'tapfile'],
      author='Simon Rowe',
      author_email='srowe@mose.org.uk',
      url='https://eden.mose.org.uk/gitweb/?p=python-cbmshell.git',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
        ]
      )
