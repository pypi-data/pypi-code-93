# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['biu', 'biu.progress', 'biu.siam_unet', 'biu.siam_unet.helpers', 'biu.unet']

package_data = \
{'': ['*']}

install_requires = \
['albumentations>=0.5.2,<0.6.0',
 'barbar>=0.2.1,<0.3.0',
 'matplotlib>=3.4.2,<4.0.0',
 'numpy>=1.19.5,<2.0.0',
 'opencv-python>=4.5.2,<5.0.0',
 'scikit-image>=0.18.2,<0.19.0',
 'scikit_image>=0.18.2,<0.19.0',
 'tifffile',
 'tqdm>=4.61.2,<5.0.0']

setup_kwargs = {
    'name': 'bio-image-unet',
    'version': '0.2.0',
    'description': 'Implementations of U-Net and Siam U-Net for biological image segmentation',
    'long_description': '# Bio Image U-Net\n\nImplementations of U-Net and Siam U-Net for biological image segmentation\n\n### Authors\n[Daniel Härtter](daniel.haertter@duke.edu) (Duke University, University of Göttingen) \\\n[Yuxi Long](longyuxi@live.com) (Duke University) \\\nAndreas Primeßnig\n\n### Installation\nInstall from [PyPI](https://pypi.org/project/bio-image-unet/): `pip install bio-image-unet`\n\n### Usage example\n[iPython Notebook for getting started with U-Net](https://github.com/danihae/bio-image-unet/blob/master/using_unet.ipynb) \\\n[iPython Notebook for getting started with Siam U-Net](https://github.com/danihae/bio-image-unet/blob/master/using_siam_unet.ipynb)\n\n### Documentation\n\nTBD',
    'author': 'Yuxi Long',
    'author_email': 'longyuxi@live.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
