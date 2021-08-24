from setuptools import setup, find_packages

l = ''
f = open('./1.txt')
for i in f.readlines():
  l+=i
f.close()
print(l)

setup(name='tic_tac_toe_api_bot',
      version='0.2',
      description='simple bot for tic tac toe',
      long_description=l,
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8',
      ],
      keywords='tic_tac_toe bot api game_api ',
      url='https://github.com/ruslan-ilesik/tic-tac-toe-bot-pip-package',
      author='lesikr',
      license='MIT',
      packages=['tic_tac_toe'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False,
      )