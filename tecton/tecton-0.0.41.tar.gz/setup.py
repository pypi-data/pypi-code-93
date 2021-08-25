import setuptools
import os

with open('README.md') as readme_f:
  long_description = readme_f.read()

packages = setuptools.find_packages()
for root, _, files in os.walk("tecton_proto"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))
for root, _, files in os.walk("protoc_gen_swagger"):
  if any([f.endswith("_pb2.py") for f in files]):
    packages.append(root.replace("/", "."))

setuptools.setup(
    classifiers=['Programming Language :: Python :: 3', 'Operating System :: OS Independent', 'License :: Other/Proprietary License'],
    python_requires='==3.7.*',
    author='Tecton, Inc.',
    author_email='support@tecton.ai',
    url='https://tecton.ai',
    license='Tecton Proprietary',
    description='Tecton Python SDK',
    entry_points={'console_scripts': ['tecton=tecton.cli.cli:main']},
    name='tecton',
    version='0.0.41',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['attrs==19.2.0', 'boto3', 'dill', 'googleapis-common-protos==1.52.0', 'grpcio', 'jinja2', '# 1.20 breaks older versions of pyarrow', '# https://stackoverflow.com/questions/67502942/arrowtypeerror-did-not-pass-numpy-dtype-object-conversion-failed-for-column', 'numpy>=1.16.5,<1.20', 'pendulum==2.0.5', 'protobuf==3.13.0', 'pytimeparse', 'pandas>=0.25.0,<=1.1.5', 'texttable', 'requests', 'colorama==0.4.3', 'tqdm==4.41.1', 'yaspin==0.16.0', 'typing-extensions==3.7.4.1', 'pygments==2.5.2', 'pyarrow==0.13.0', 'pytest==5.4.3', 'click==7.1.2', 'typeguard'],
    extras_require={'databricks-connect': ['databricks_connect~=6.4.28'], 'pyspark': ['pyspark==2.4.4']},
    packages=packages,
)
