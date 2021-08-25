# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kaldigrpc_client', 'kaldigrpc_client.generated']

package_data = \
{'': ['*']}

install_requires = \
['grpcio-tools>=1.39.0,<2.0.0',
 'grpcio>=1.39.0,<2.0.0',
 'pydub>=0.25.1,<0.26.0']

entry_points = \
{'console_scripts': ['kaldigrpc-transcribe = '
                     'kaldigrpc_client.client:transcribe_wav']}

setup_kwargs = {
    'name': 'kaldigrpc-client',
    'version': '0.2.0',
    'description': 'Python client for Kaldi GRPC server',
    'long_description': '# Kaldi gRPC client\n\nPython client library for Kaldi gRPC server. This client has similar - identical - semantics to the\n[Google speech Python library](https://cloud.google.com/speech-to-text/docs/libraries#client-libraries-install-python).\n\n\n## Installation\n\nYou can install from source\n\n```bash\ngit clone https://github.com/georgepar/kaldi-grpc-server\ncd client\npip install .\n```\n\nor from Pypi\n\n```bash\npip install kaldigrpc-client\n```\n\n## Usage from command line\n\nWe assume you have a server running on port `50051`. See `kaldi-grpc-server` README for more\ninformation.\n\n```bash\nkaldigrpc-transcribe --port 50051 $MY_WAV_FILE\n```\n\nFor long files we recommend using the streaming client\n\n\n```bash\nkaldigrpc-transcribe --streaming --port 50051 $MY_WAV_FILE\n```\n\n## Programmatic usage\n\nThe following is a simple example for streaming recognition using the ILSPASRClient.\nYou can also refer to the code and the proto files for more configuration options and more outputs\n(e.g. confidence, word start and end times etc.)\n\n**Warning**: Some configuration options are included for compatibility / easy swapping with the Google Speech\nclient library but are not yet fully implemented. Please refer to the code for more details.\n\n```python\ncli = ILSPASRClient(host="localhost", port=50051)\n\nchunks = ...  # list of audio chunks (bytes)\n\nfor partial_result in cli.streaming_recognize(chunks):\n    # Print best path partial transcription\n    print(partial_result.results[0].alternatives[0].transcript)\n```\n',
    'author': 'Giorgos Paraskevopoulos',
    'author_email': 'geopar@central.ntua.gr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/georgepar/kaldi-grpc-server',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
