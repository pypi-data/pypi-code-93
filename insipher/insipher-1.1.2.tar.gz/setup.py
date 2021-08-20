from setuptools import setup

setup(name='insipher',
      version='1.1.2',
      description='Insipher Python SDK',
      packages=['insipher'],
      author="Insipher",
      author_email='info@insipher.com',
      license='MIT',
      url='https://www.insipher.com',
      install_requires=[
            'uvicorn==0.13.4',
            'fastapi==0.63.0',
            'minio==7.0.2',
            'pyyaml==5.4.1',
      ],
      zip_safe=False)
