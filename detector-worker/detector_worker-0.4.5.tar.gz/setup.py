from setuptools import setup

setup(name='detector_worker',
      version='0.4.5',
      description='Worker class for incapsulating logic, required for Lionbridge Rnd detectors',
      url='https://liox-teams.visualstudio.com/LE%20Research/_git/DntExtractor',
      author='Rodion Cherny',
      author_email='v-Rodion.Cherny@lionbridge.com',
      license='MIT',
      packages=['detector_worker'],
      install_requires=[
          'azure-storage-blob==12.5.0',
          'azure-cosmosdb-table==1.0.6',
          'azure-storage-queue==12.1.2',
          'spacy==2.3.0'
      ],
      zip_safe=False)


# python setup.py sdist bdist_wheel
# python -m twine upload  dist/*