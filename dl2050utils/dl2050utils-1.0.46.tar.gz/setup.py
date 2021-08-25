from distutils.core import setup

# setup(name='utils',
#       version='1.0.46',
#       description='utils lib',
#       author='João Neto',
#       author_email='joao.filipe.neto@gmail.com',
#       packages=['utils'],
# )

setup(name='dl2050utils',
      packages=['dl2050utils'],
      version='1.0.46',
      license='MIT',
      description='Utils lib',
      author='João Neto',
      author_email='joao.filipe.neto@gmail.com',
      keywords=['utils'],
      url='https://github.com/jn2050/utils',
      download_url='https://github.com/jn2050/utils/archive/v_1_0_46.tar.gz',
      # install_requires=[
      #       'pathlib',
      #       'zipfile',
      #       'json',
      #       'socket',
      #       'smtplib',
      #       'ssl',
      #       'boto3',
      #       'asyncpg',
      #       '',
      # ],
      classifiers=[
            'Development Status :: 4 - Beta',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.7',
      ],
)
