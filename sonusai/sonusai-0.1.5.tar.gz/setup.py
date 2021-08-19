# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sonusai']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0',
 'h5py>=2.10.0,<2.11.0',
 'keras2onnx>=1.7.0,<2.0.0',
 'matplotlib>=3.3.1,<4.0.0',
 'sklearn>=0.0,<0.1',
 'sox>=1.4.1,<2.0.0']

setup_kwargs = {
    'name': 'sonusai',
    'version': '0.1.5',
    'description': 'Framework for building deep neural network models for sound, speech, and voice AI',
    'long_description': "Sonus AI: Framework for simplified creation of deep NN models for sound, speech, and voice AI\n\nSonus AI includes functions for pre-processing training and validation data and\ncreating performance metrics reports for key types of Keras models:\n- recurrent, convolutional, or a combination (i.e. RCNNs)\n- binary, multiclass single-label, multiclass multi-label, and regresssion\n- training with data augmentations:  noise mixing, pitch and time stretch, etc.\n\nSonus AI python functions are used by:\n - Aaware Inc. sonusai executable:  Easily create train/validation data, run prediction, evaluate model performance\n - Keras model scripts:             User python scripts for keras model creation, training, and prediction. These can use sonusai-specific data but also some general useful utilities for trainining rnn-based models like CRNN's, DSCRNN's, etc. in Keras\n",
    'author': 'Chris Eddington',
    'author_email': 'chris@aaware.com',
    'maintainer': 'Chris Eddington',
    'maintainer_email': 'chris@aaware.com',
    'url': 'http://aaware.com',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
