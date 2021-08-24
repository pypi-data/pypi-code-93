# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['biopsykit',
 'biopsykit.carwatch_logs',
 'biopsykit.classification',
 'biopsykit.classification.model_selection',
 'biopsykit.colors',
 'biopsykit.io',
 'biopsykit.metadata',
 'biopsykit.plotting',
 'biopsykit.protocols',
 'biopsykit.questionnaires',
 'biopsykit.saliva',
 'biopsykit.signals',
 'biopsykit.signals.ecg',
 'biopsykit.signals.eeg',
 'biopsykit.signals.imu',
 'biopsykit.signals.imu.feature_extraction',
 'biopsykit.signals.rsp',
 'biopsykit.sleep',
 'biopsykit.sleep.psg',
 'biopsykit.sleep.sleep_endpoints',
 'biopsykit.sleep.sleep_processing_pipeline',
 'biopsykit.sleep.sleep_wake_detection',
 'biopsykit.sleep.sleep_wake_detection.algorithms',
 'biopsykit.stats',
 'biopsykit.utils']

package_data = \
{'': ['*']}

install_requires = \
['XlsxWriter>=1.4.5,<2.0.0',
 'joblib>=1.0.0,<2.0.0',
 'matplotlib>=3,<4',
 'neurokit2>=0.1.3,<0.2.0',
 'nilspodlib>=3.2.2,<4.0.0',
 'numpy>=1,<2',
 'openpyxl>=3.0.7,<4.0.0',
 'pandas>=1.2.0,<2.0.0',
 'pingouin>=0.3.12,<0.4.0',
 'scikit-learn>=0.24.2,<0.25.0',
 'scipy>=1.7.1,<2.0.0',
 'seaborn>=0.11.1,<0.12.0',
 'statannot>=0.2.3,<0.3.0',
 'statsmodels>=0.12.2,<0.13.0',
 'tqdm>=4.62.0,<5.0.0',
 'xlrd>=2.0.1,<3.0.0']

extras_require = \
{'jupyter': ['IPython>=7.13.0,<8.0.0',
             'ipywidgets>=7.6.3,<8.0.0',
             'ipympl>=0.7.0,<0.8.0'],
 'mne': ['mne>=0.23.0,<0.24.0']}

setup_kwargs = {
    'name': 'biopsykit',
    'version': '0.2.3',
    'description': 'A python package for the analysis of biopsychological data.',
    'long_description': '# BioPsyKit\n\n[![PyPI](https://img.shields.io/pypi/v/biopsykit)](https://pypi.org/project/biopsykit/)\n![GitHub](https://img.shields.io/github/license/mad-lab-fau/biopsykit)\n[![Test and Lint](https://github.com/mad-lab-fau/BioPsyKit/actions/workflows/test-and-lint.yml/badge.svg)](https://github.com/mad-lab-fau/BioPsyKit/actions/workflows/test-and-lint.yml)\n![Coverage](./coverage-badge.svg)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n![PyPI - Downloads](https://img.shields.io/pypi/dm/biopsykit)\n![GitHub commit activity](https://img.shields.io/github/commit-activity/m/mad-lab-fau/biopsykit)\n\nA Python package for the analysis of biopsychological data.\n\nWith this package you have everything you need for analyzing biopsychological data, including:\n* Data processing pipelines for various physiological signals (ECG, EEG, Respiration, Motion, ...).\n* Algorithms and data processing pipelines for sleep/wake prediction and computation of sleep endpoints \n  based on activity or IMU data.\n* Functions to import and process data from sleep trackers (e.g., Withings Sleep Analyzer)\n* Functions for processing and analysis of salivary biomarker data (cortisol, amylase).\n* Implementation of various psychological and HCI-related questionnaires.\n* Implementation of classes representing different psychological protocols \n  (e.g., TSST, MIST, Cortisol Awakening Response Assessment, etc.)\n* Functions for easily setting up statistical analysis pipelines.\n* Functions for setting up and evaluating machine learning pipelines.\n* Plotting wrappers optimized for displaying biopsychological data.\n\n## Details\n\n### Analysis of Physiological Signals\n#### ECG Processing\n`BioPsyKit` provides a whole ECG data processing pipeline, consisting of:\n* Loading ECG data from:\n    * Generic `.csv` files\n    * NilsPod binary (`.bin`) files (requires `NilsPodLib`: https://github.com/mad-lab-fau/NilsPodLib)\n    * Other sensor types (_coming soon_)\n* Splitting data into single parts (based on time intervals) that will be analyzed separately\n* Perform ECG processing, including:\n    * R peak detection (using `Neurokit`: https://github.com/neuropsychology/NeuroKit)\n    * R peak outlier removal and interpolation\n    * HRV feature computation\n    * ECG-derived respiration (EDR) estimation for respiration rate and respiratory sinus arrhythmia (RSA) \n      (_experimental_)\n    * Resample instantaneous heart rate data \n    * Compute aggregated results (e.g., mean and standard error) per part\n* Create plots for visualizing processing results\n\n... more biosignals coming soon!\n\n### Sleep/Wake Prediction\n`BioPsyKit` allows to process sleep data collected from IMU or activity sensors (e.g., Actigraphs). This includes:\n* Detection of wear periods\n* Detection of time spent in bed\n* Detection of sleep and wake phases\n* Computation of sleep endpoints (e.g., sleep and wake onset, net sleep duration wake after sleep onset, etc.)\n\n\n#### Quick Example\n```python\nimport biopsykit as bp\nfrom biopsykit.example_data import get_sleep_imu_example\n\nimu_data, sampling_rate = get_sleep_imu_example()\n\nsleep_results = bp.sleep.sleep_processing_pipeline.predict_pipeline_acceleration(imu_data, sampling_rate)\nsleep_endpoints = sleep_results["sleep_endpoints"]\n\nprint(sleep_endpoints)\n```\n\n### Salivary Biomarker Analysis\n`BioPsyKit` provides several methods for the analysis of salivary biomarkers (e.g. cortisol and amylase), such as:\n* Import data from Excel and csv files into a standardized format\n* Compute standard features (maximum increase, slope, area-under-the-curve, mean, standard deviation, ...)\n\n#### Quick Example\n```python\nimport biopsykit as bp\nfrom biopsykit.example_data import get_saliva_example\n\nsaliva_data = get_saliva_example(sample_times=[-20, 0, 10, 20, 30, 40, 50])\n\nmax_inc = bp.saliva.max_increase(saliva_data)\n# remove the first saliva sample (t=-20) from computing the AUC\nauc = bp.saliva.auc(saliva_data, remove_s0=True)\n\nprint(max_inc)\nprint(auc)\n```\n\n### Questionnaires\n`BioPsyKit` implements various established psychological and HCI-related questionnaires, such as:\n* Perceived Stress Scale (PSS)\n* Positive Appraisal Negative Appraisal Scale (PANAS)\n* Self-Compassion Scale (SCS)\n* Big Five Inventory (BFI)\n* State Trait Depression and Anxiety Questionnaire (STADI)\n* Trier Inventory for Chronic Stress (TICS)\n* System Usability Scale (SUS)\n* NASA Task Load Index (NASA-TLX)\n* Short Stress State Questionnaire (SSSQ)\n* ...\n\n#### Quick Example\n```python\nimport biopsykit as bp\nfrom biopsykit.example_data import get_questionnaire_example\n\ndata = get_questionnaire_example()\n\npss_data = data.filter(like="PSS")\npss_result = bp.questionnaires.pss(pss_data)\n\nprint(pss_result)\n```\n\n### Psychological Protocols\n`BioPsyKit` implements methods for easy handling and analysis of data recorded with several established psychological \nprotocols, such as:\n* Montreal Imaging Stress Task (MIST)\n* Trier Social Stress Test (TSST)\n* Cortisol Awakening Response Assessment (CAR)\n* ...\n\n#### Quick Example\n```python\nfrom biopsykit.protocols import TSST\nfrom biopsykit.example_data import get_saliva_example\nfrom biopsykit.example_data import get_mist_hr_example\n# specify TSST structure and the durations of the single phases\nstructure = {\n   "Pre": None,\n   "TSST": {\n       "Preparation": 300,\n       "Talk": 300,\n       "Math": 300\n   },\n   "Post": None\n}\ntsst = TSST(name="TSST", structure=structure)\n\nsaliva_data = get_saliva_example(sample_times=[-20, 0, 10, 20, 30, 40, 50])\nhr_data = get_mist_hr_example()\n# add saliva data collected during the whole TSST procedure\ntsst.add_saliva_data(saliva_data, saliva_type="cortisol")\n# add heart rate data collected during the "TSST" study part\ntsst.add_hr_data(hr_data, study_part="TSST")\n```\n\n## Installation\n```\npip install biopsykit\n```\n\n\n### For Developer\n\n#### Without Extras\n```bash\ngit clone https://github.com/mad-lab-fau/BioPsyKit.git\ncd biopsykit\npoetry install\n```\n\n#### With all Extras (e.g., extended functionalities for IPython/Jupyter Notebooks)\n```bash\ngit clone https://github.com/mad-lab-fau/BioPsyKit.git\ncd biopsykit\npoetry install -E mne -E jupyter \n```\nInstall Python >=3.7 and [poetry](https://python-poetry.org).\nThen run the commands below to get the latest source and install the dependencies:\n\n\nTo run any of the tools required for the development workflow, use the `doit` commands:\n\n```bash\n$ poetry run doit list\ndocs                 Build the html docs using Sphinx.\nformat               Reformat all files using black.\nformat_check         Check, but not change, formatting using black.\nlint                 Lint all files with Prospector.\ntest                 Run Pytest with coverage.\nupdate_version       Bump the version in pyproject.toml and biopsykit.__init__ .\n```\n\n\n## Examples\nSee Examples in the function documentations on how to use this library.\n',
    'author': 'Robert Richer',
    'author_email': 'robert.richer@fau.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mad-lab-fau/biopsykit',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7.1,<3.10',
}


setup(**setup_kwargs)
