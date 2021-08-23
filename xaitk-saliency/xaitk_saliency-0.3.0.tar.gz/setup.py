# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xaitk_saliency',
 'xaitk_saliency.impls',
 'xaitk_saliency.impls.gen_classifier_conf_sal',
 'xaitk_saliency.impls.gen_descriptor_sim_sal',
 'xaitk_saliency.impls.gen_image_classifier_blackbox_sal',
 'xaitk_saliency.impls.perturb_image',
 'xaitk_saliency.interfaces',
 'xaitk_saliency.utils']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.4.1,<4.0.0',
 'numpy>=1.20.3,<2.0.0',
 'opencv-python-headless>=4.5.1,<5.0.0',
 'scikit-image>=0.18.1,<0.19.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.6.3,<2.0.0',
 'smqtk-classifier>=0.17.0',
 'smqtk-core>=0.18.0',
 'smqtk-descriptors>=0.16.0',
 'tqdm>=4.60.0,<5.0.0']

extras_require = \
{'example_deps': ['jupyter>=1.0.0,<2.0.0',
                  'torch>=1.9.0,<2.0.0',
                  'torchvision>=0.10.0,<0.11.0']}

entry_points = \
{'smqtk_plugins': ['impls.gen_classifier_conf_sal.occlusion_scoring = '
                   'xaitk_saliency.impls.gen_classifier_conf_sal.occlusion_scoring',
                   'impls.gen_classifier_conf_sal.rise_scoring = '
                   'xaitk_saliency.impls.gen_classifier_conf_sal.rise_scoring',
                   'impls.gen_descriptor_sim_sal.similarity_scoring = '
                   'xaitk_saliency.impls.gen_descriptor_sim_sal.similarity_scoring',
                   'impls.gen_image_classifier_blackbox_sal.occlusion_based = '
                   'xaitk_saliency.impls.gen_image_classifier_blackbox_sal.occlusion_based',
                   'impls.gen_image_classifier_blackbox_sal.rise = '
                   'xaitk_saliency.impls.gen_image_classifier_blackbox_sal.rise',
                   'impls.perturb_image.occlusion = '
                   'xaitk_saliency.impls.perturb_image.sliding_window',
                   'impls.perturb_image.rise = '
                   'xaitk_saliency.impls.perturb_image.rise']}

setup_kwargs = {
    'name': 'xaitk-saliency',
    'version': '0.3.0',
    'description': 'Visual saliency map generation interfaces and baseline implementations for explainable AI.',
    'long_description': '# XAITK - Saliency\n\n## Intent\nProvide interfaces that convey a standard API for visual saliency\nmap generation.\n\n## Documentation\nhttps://xaitk-saliency.readthedocs.io/en/latest/\n\nYou can also build the sphinx documentation locally for the most up-to-date\nreference:\n```bash\n# Install dependencies\npoetry install\n# Navigate to the documentation root.\ncd docs\n# Build the docs.\npoetry run make html\n# Open in your favorite browser!\nfirefox _build/html/index.html\n```\n',
    'author': 'Kitware, Inc.',
    'author_email': 'xaitk@kitware.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/XAITK/xaitk-saliency',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
